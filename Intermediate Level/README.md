# AI-Powered Document-Based QA Assistant

## Problem Statement
Students and researchers often need to parse through dense, lengthy documents (like research papers, textbooks, or lecture notes) to find specific information. Generic large language models (LLMs) can answer general questions but are not aware of the specific contents of these user-provided documents, often leading to hallucinations or incorrect information. There is a need for a targeted AI assistant that can strictly answer questions based *only* on the provided text, ensuring accuracy and reliability.

## Objective
The objective of this project is to build a practical Retrieval-Augmented Generation (RAG) workflow. This system allows users to upload multiple PDF or text documents, process them into searchable chunks, and ask questions. The system will retrieve relevant context from the uploaded documents and generate an accurate, grounded answer, completely avoiding hallucinated responses.

## Proposed Methodology
The application follows a standard Retrieval-Augmented Generation (RAG) architecture:
1. **Document Ingestion:** Text is extracted from uploaded `.pdf` or `.txt` files using LangChain's `PyPDFLoader` and `TextLoader`.
2. **Chunking Strategy:** The extracted text is split into smaller, meaningful segments using a `RecursiveCharacterTextSplitter`. A chunk size of 1000 characters with an overlap of 200 characters is used to ensure context is not lost across chunk boundaries.
3. **Embedding Generation:** The chunks are converted into vector representations using either OpenAI embeddings or local HuggingFace embeddings (`all-MiniLM-L6-v2`).
4. **Vector Storage:** The embeddings are stored in a Chroma vector database configured for cosine similarity search.
5. **Retrieval & Grounding:** When a user asks a question, the system retrieves the top 3 most relevant chunks. A strict confidence threshold is applied (e.g., rejecting matches with a distance > 0.85 for HuggingFace) to ensure the question is actually covered by the document.
6. **Answer Generation:** The retrieved context is injected into a strict prompt template, instructing the LLM (OpenAI or Qwen) to answer *only* based on the context provided.

## How the Application Works (AI-Assisted Student Workflow)
Unlike a generic chatbot that relies on pre-trained memory and might hallucinate facts, this application acts as a strict **AI-assisted study companion**. 

- **Prompt Structure:** The LLM is restricted using the following strict prompt:
  ```text
  You are an expert assistant. Use ONLY the following retrieved context to answer the user's question.
  If you do not know the answer based on the context, say "I cannot find the answer in the provided document." Do not make up an answer.
  ```
- **Error Handling:** The application gracefully handles common errors:
  - **Irrelevant Queries:** If a student asks a question entirely unrelated to the uploaded document, the system's vector search distance will exceed the confidence threshold, and the app will actively refuse to answer, explaining that the text does not contain a close match.
  - **API/Billing Issues:** Specific error catching is implemented to notify users if their OpenAI API key is invalid or if their account has run out of credits, seamlessly offering the free local HuggingFace fallback.
  - **Empty/Invalid Uploads:** The UI prevents processing if no files are uploaded or if queries are completely empty.
- **Student Workflow:** A student can upload a chapter of a textbook, ask a specific question, and not only receive the answer but also view the exact source paragraphs (via Streamlit expanders) that the AI used to generate the answer. This builds trust and allows the student to verify the information.

## Folder Structure
```text
RAG/
├── app.py                      # Main Streamlit frontend application
├── backend_logic.py            # Core RAG pipeline, embedding, and LLM logic
├── requirements.txt            # Python dependencies
├── setup_and_run.bat           # Windows Batch script for automated setup
├── setup_and_run.ps1           # PowerShell script for automated setup
└── README.md                   # Project documentation
```

## Running Commands (Setup Instructions)
To run this project on a fresh machine:

### Prerequisites
1. **Python 3.9+**: Ensure Python is installed and added to your system PATH.
2. **Git** (Optional): To clone the repository.

### Installation & Execution
**Option 1: Automated Setup (Windows)**
Simply double-click the `setup_and_run.bat` file. It will automatically create a virtual environment, install all dependencies from `requirements.txt`, and launch the application.

**Option 2: Manual Setup (Any OS)**
Open a terminal/command prompt and run the following commands sequentially:

1. **Clone or download the project folder and navigate to it:**
   ```bash
   cd path/to/RAG
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

## Results
The system successfully processes both text and PDF documents, creating highly accurate semantic chunks. When queried, it accurately retrieves the relevant paragraphs and synthesizes an answer. If queried about out-of-context topics (e.g., asking about "Python" when a document about "Biology" is uploaded), the system correctly triggers the confidence threshold and refuses to answer, successfully preventing hallucinations. The UI provides a clean, fast, and intuitive experience.

## Conclusion
This project successfully demonstrates an industrial-grade, practical implementation of a Document QA Assistant using the RAG architecture. By combining advanced chunking strategies, strict prompt engineering, similarity distance thresholds, and source visibility, it serves as a robust and reliable tool for students and professionals to interact with their documents.
