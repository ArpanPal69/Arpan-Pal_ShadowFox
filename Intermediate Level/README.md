# 🧠 AI-Powered Document-Based QA Assistant

## 🛑 Problem Statement
Students and researchers often need to parse through dense, lengthy documents (like research papers, textbooks, or lecture notes) to find specific information. Generic large language models (LLMs) can answer general questions but are not aware of the specific contents of these user-provided documents, often leading to hallucinations or incorrect information. There is a need for a targeted AI assistant that can strictly answer questions based *only* on the provided text, ensuring accuracy and reliability.

## 🎯 Objective
The objective of this project is to build a practical Retrieval-Augmented Generation (RAG) workflow. This system allows users to upload multiple PDF or text documents, process them into searchable chunks, and ask questions. The system will retrieve relevant context from the uploaded documents and generate an accurate, grounded, and intelligently synthesized answer, completely avoiding hallucinated responses.

## 🛠️ System Architecture & Technical Methodology
The application follows an advanced Retrieval-Augmented Generation (RAG) architecture. Below is a detailed explanation of how the retrieval flow is structured and how each component operates:

### 1. Document Ingestion
Text is extracted from uploaded `.pdf` or `.txt` files using LangChain's `PyPDFLoader` and `TextLoader`. The system allows multiple documents to be uploaded and processed into the same active session simultaneously.

### 2. Chunking Strategy
The extracted text is split into smaller, meaningful segments using a `RecursiveCharacterTextSplitter`. 
- **Chunk Size (1000 characters):** Chosen because it is large enough to capture full paragraphs and complete contextual ideas.
- **Chunk Overlap (200 characters):** Chosen to ensure that sentences or concepts that straddle the boundary between two chunks are not lost. This overlap maintains semantic continuity during search.

### 3. Embedding & Vector Search Approach
- **Embeddings:** The chunks are converted into dense vector representations. Users can dynamically switch between OpenAI embeddings or free local HuggingFace embeddings (`all-MiniLM-L6-v2`). 
- **Vector Database:** The embeddings are stored in an in-memory **ChromaDB** instance configured for **cosine similarity** space.
- **Retrieval:** When a user asks a question, it is embedded, and the system performs an approximate nearest-neighbor search. We retrieve the top 8 chunks (`k=8`) to ensure a broad enough context window, allowing the AI to answer comprehensive questions (e.g., summarizing an entire document) without missing distant information.

### 4. Grounding Mechanisms & Hallucination Reduction
To ensure the final answer remains strictly tied to the document and does not drift into unsupported outputs, the system employs two distinct layers of protection:
- **Confidence Thresholding (Distance Check):** Before generating an answer, the system evaluates the mathematical distance of the best-matching chunk. If the cosine distance is too high (e.g., > 0.85 for HuggingFace embeddings), it means the document does not contain relevant information. The system will actively refuse to answer rather than making a guess.
- **Strict Prompt Engineering:** The retrieved context is injected into a strict prompt template. The LLM is explicitly instructed to:
  1. Use ONLY the retrieved context.
  2. Synthesize and summarize intelligently (avoiding blind copy-pasting).
  3. Respond with "I cannot find the answer" if the context is insufficient.

### 5. Application Structuring & UI
The frontend is built with **Streamlit** to provide a usable, intuitive AI-assisted student workflow. It handles invalid files and empty queries gracefully, catches API billing errors dynamically, and most importantly, features **Source Context Visibility**—users can expand accordions to read the exact raw chunks the AI used to formulate its answer, building complete trust in the system.

## 📂 Folder Structure
```text
RAG/
├── app.py                      # Main Streamlit frontend application
├── backend_logic.py            # Core RAG pipeline, embedding, and LLM logic
├── find_models.py              # Script to identify compatible models
├── test_pipeline.py            # Pipeline testing script
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## 🚀 Running Commands (Setup Instructions)
To run this project on a fresh machine:

### Prerequisites
1. **Python 3.9+**: Ensure Python is installed and added to your system PATH.
2. **Git** (Optional): To clone the repository.

### Installation & Execution
Open a terminal/command prompt and run the following commands sequentially:

1. **Clone or download the project folder and navigate to it:**
   ```bash
   cd path/to/your/project/RAG
   ```
2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
4. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

The application will open in your default web browser at `http://localhost:8501`.

## 📊 Results
The system successfully processes both text and PDF documents, creating highly accurate semantic chunks. When queried, it accurately retrieves the relevant paragraphs and intelligently synthesizes an answer without copy-pasting. If queried about out-of-context topics (e.g., asking about "Python" when a document about "Biology" is uploaded), the system correctly triggers the confidence threshold and refuses to answer, successfully preventing hallucinations. The UI provides a clean, fast, and intuitive experience.

## 🏁 Conclusion
This project successfully demonstrates an industrial-grade, practical implementation of a Document QA Assistant using the RAG architecture. By combining advanced chunking strategies, strict prompt engineering, similarity distance thresholds, and source visibility, it serves as a robust and reliable tool for students and professionals to interact with their documents.
