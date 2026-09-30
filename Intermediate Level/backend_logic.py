import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import pipeline

class RAGPipeline:
    def __init__(self, api_key: str = None, model_type: str = "OpenAI", openrouter_model: str = None):
        self.api_key = api_key
        self.model_type = model_type
        
        if model_type == "OpenAI":
            if not api_key:
                raise ValueError("OpenAI API key is required for OpenAI models.")
            self.embeddings_model = OpenAIEmbeddings(openai_api_key=api_key)
            self.llm = ChatOpenAI(temperature=0, openai_api_key=api_key)
        elif model_type == "OpenRouter":
            if not api_key:
                raise ValueError("OpenRouter API key is required.")
            # Use local embeddings to ensure compatibility and keep it free
            self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # Fallback to a known free model if none provided
            or_model = openrouter_model if openrouter_model else "openrouter/free"
            self.llm = ChatOpenAI(
                model=or_model,
                temperature=0, 
                openai_api_key=api_key, 
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/",
                    "X-Title": "RAG Assistant"
                }
            )
        elif model_type == "HuggingFace (Local)":
            # Local embeddings (downloaded automatically)
            self.embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # Local LLM pipeline (using a relatively small model to avoid huge downloads)
            # Qwen 0.5B is a small, highly capable decoder-only model perfectly suited for text-generation.
            hf_pipeline = pipeline(
                "text-generation", 
                model="Qwen/Qwen2.5-0.5B-Instruct", 
                max_new_tokens=256,
                return_full_text=False
            )
            self.llm = HuggingFacePipeline(pipeline=hf_pipeline)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # In-memory temporary directory for Chroma DB (auto-cleans on exit)
        self._temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.persist_directory = self._temp_dir.name
        
        # Configure Chroma to use cosine distance
        self.vector_store = Chroma(
            embedding_function=self.embeddings_model,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )

    def process_document(self, file_path: str, original_filename: str):
        """Handles Ingestion, Chunking, and Embedding"""
        if original_filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif original_filename.lower().endswith(".txt"):
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError("Unsupported file format. Please upload a PDF or TXT file.")
            
        documents = loader.load()
        
        # Chunking Strategy: 
        # - chunk_size=1000 characters: Large enough to capture full paragraphs and context.
        # - chunk_overlap=200 characters: Ensures that sentences/ideas split across boundaries are not lost.
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            raise ValueError("No text could be extracted from the document.")
            
        # Store in Chroma
        self.vector_store.add_documents(chunks)
        return "Document processed and indexed successfully."

    def answer_query(self, user_query: str):
        """Handles Retrieval, Prompting, and Generation with Confidence Scoring"""
        # Similarity search (k=8 to ensure broader context retrieval for comprehensive questions)
        docs_with_scores = self.vector_store.similarity_search_with_score(user_query, k=8)
        
        context_text = ""
        sources = []
        
        if not docs_with_scores:
            return {
                "answer": "No relevant documents found.",
                "sources": []
            }
            
        # For cosine distance, lower is better (0 is exact match, 1 is completely different)
        best_distance = min([score for doc, score in docs_with_scores])
        
        for doc, score in docs_with_scores:
            context_text += f"{doc.page_content}\n\n"
            sources.append(doc.page_content)
            
        # Confidence Threshold Check: 
        # Different embedding models have different baseline distances for "good" matches.
        # all-MiniLM-L6-v2 often has distances ranging from 0.6 to 0.8 for valid semantic matches.
        threshold = 0.35 if self.model_type == "OpenAI" else 0.85
        
        # If the best match distance is > threshold (meaning similarity is low), reject answering.
        if best_distance > threshold:
            return {
                "answer": f"I cannot confidently answer this based on the uploaded document. The available text does not provide a close enough match to your query. (Best distance: {best_distance:.2f}, Threshold: {threshold})",
                "sources": []
            }

        # Strict Grounding Prompt with Synthesis Instructions
        prompt_template = """
You are an expert AI assistant. Use ONLY the following retrieved context to answer the user's question.
If you do not know the answer based on the context, say "I cannot find the answer in the provided document." Do not make up an answer.

Important Instructions:
- Do not simply copy and paste sentences verbatim from the context.
- Use your intelligence to synthesize, summarize, and explain the information in your own words.
- Structure your answer clearly (using headings or bullet points if it helps) to make it highly readable.
- Maintain a helpful, conversational tone while staying 100% factual to the provided text.

Context:
{context}

Question: {question}
Answer:
"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = prompt | self.llm
        
        response = chain.invoke({"context": context_text, "question": user_query})
        
        # OpenAI returns an AIMessage with a .content attribute, while HuggingFace returns a raw string
        answer_text = response.content if hasattr(response, "content") else str(response)
        
        return {
            "answer": answer_text,
            "sources": sources
        }
