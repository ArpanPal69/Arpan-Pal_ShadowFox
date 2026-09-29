# 🚀 Advanced Agentic Retrieval-Augmented Generation (RAG) System

## 🎯 1. Problem Statement
Traditional Retrieval-Augmented Generation (RAG) models often follow a naive, linear path: **User Query $\rightarrow$ Vector Search $\rightarrow$ LLM $\rightarrow$ Output**. While effective for basic prototypes, this approach is fundamentally flawed for production environments. If the vector search returns irrelevant or noisy context, the Language Model will hallucinate an answer based on that incorrect data. Standard RAG lacks the ability to self-reflect, grade its own retrieved context, or self-correct when things go wrong, leading to unreliable systems that cannot be trusted in real-world LLM product development.

## 💡 2. Objective
The objective of this project is to build an **Advanced, Production-Style Agentic RAG System**. Moving beyond a simple demo application, this project implements a complete AI engineering architecture that features multi-stage reasoning, relevance grading, automated query rewriting, and strict hallucination prevention. The goal is to provide highly accurate, strictly grounded answers with verifiable citations over complex, multi-format documents (PDF, TXT, Markdown).

## 🧠 3. Proposed Methodology & Architecture (Self-Reflective CRAG)
This system was engineered to strictly satisfy every requirement of an Advanced-Level AI pipeline. To solve the hallucination problem and improve retrieval quality, we implemented a **Corrective RAG (CRAG)** agentic workflow utilizing **LangGraph**. 

Here is exactly how the architecture maps to the core requirements:

*   📄 **Multi-format document ingestion & Preprocessing:** The system dynamically routes and parses PDF, TXT, and Markdown files using robust LangChain loaders.
*   ✂️ **Chunking strategy:** We utilize a `RecursiveCharacterTextSplitter` (chunk size 500, overlap 50) to accurately preserve the semantic boundaries of paragraphs during parsing.
*   🧠 **Embedding generation & Vector indexing:** We use HuggingFace's lightweight `all-MiniLM-L6-v2` to generate dense vectors, which are then indexed locally using **FAISS** for blazing-fast vector search.
*   🔍 **Document-scoped retrieval:** Searches can be explicitly filtered to specific uploaded documents, eliminating global database noise.
*   📈 **Reranking (Retrieval Improvement Logic):** FAISS handles the broad search, but we implemented a **Cross-Encoder Reranker** (`ms-marco-MiniLM-L-6-v2`) to deeply analyze and sort the top chunks by absolute contextual relevance, vastly improving retrieval quality.
*   ⚖️ **Agentic Workflow (Grading & Rewriting):** Instead of a linear script, a LangGraph agent takes over:
    *   **Grade:** An LLM explicitly evaluates the retrieved chunks. If irrelevant, it rejects them.
    *   **Query rewriting:** If chunks are rejected, the agent assumes the user's query was suboptimal, rewrites it for better semantic matching, and re-retrieves automatically.
*   🛡️ **Validation using Typed Schemas:** **Pydantic** is heavily utilized across the **FastAPI** backend to ensure strict data validation (e.g., rejecting empty queries), demonstrating robust reliability thinking.

## 📂 4. Folder Structure (Clean API & App Structure)
The project features a strict separation of concerns, dividing the backend engine from the frontend presentation layer.
```text
Agentic-RAG/
│
├── backend/
│   ├── agent.py               # LangGraph multi-step agent logic (Retrieve, Grade, Generate, Check)
│   ├── config.py              # Environment configuration
│   ├── document_loader.py     # Parsing, preprocessing, and chunking logic
│   ├── faiss_retriever.py     # Embeddings, FAISS indexing, and Cross-Encoder reranking
│   ├── main.py                # FastAPI endpoints
│   ├── schemas.py             # Pydantic validation models
│   └── Dockerfile             # Containerization
│
├── frontend/
│   ├── app.py                 # Streamlit UI
│   └── Dockerfile             # Containerization
│
├── docker-compose.yml         # Container orchestration
├── start.bat                  # One-click Windows setup
├── start.sh                   # One-click Mac/Linux setup
└── README.md                  
```

## 💻 5. Running Commands
We have engineered this project for **reproducibility** and easy setup on any machine.

### Option 1: One-Click Local Setup (Windows)
Automatically creates a `venv`, installs dependencies, and boots the servers.
```cmd
start.bat
```

### Option 2: One-Click Local Setup (Linux / Mac)
```bash
chmod +x start.sh
./start.sh
```

### Option 3: Containerized Setup (Docker)
For a completely isolated production environment:
```bash
docker-compose up --build
```

⚠️ **Note on API Keys (Crucial):** This project is currently configured to use **OpenRouter** as the LLM routing provider to access the `gpt-4o-mini` model. Once the Streamlit interface opens at `http://localhost:8501`, you must enter an **OpenRouter API Key** (which starts with `sk-or-v1-...`) in the sidebar. You can generate a key here: [https://openrouter.ai/](https://openrouter.ai/). The system securely injects this key directly into the agent's state per-request, preventing data leakage.

## 📊 6. Results & Observability
The implemented system drastically outperforms standard demo applications:
*   ✅ **Grounded Answer Generation:** The LLM is strictly constrained via prompting to generate answers *only* using the approved context.
*   🚫 **Hallucinations Reduced:** A final "Hallucination Check" node mathematically evaluates the generated answer against the source text. If the agent detects that it made up facts, it refuses to answer.
*   🔎 **Context Display & Citation Support:** The UI features an expandable section showing the exact source document, page number, and raw text chunk used to construct the answer.
*   ⚡ **Streaming/Responsive Delivery:** The Streamlit frontend utilizes a custom text-streaming generator, typing out the final answer dynamically to provide a highly responsive, ChatGPT-like user experience.
*   👀 **Observability:** Users are shown a transparent breakdown of the LangGraph agent's internal "thinking" steps (e.g., grading, rewriting, checking).

## 🎓 7. Conclusion
This project successfully transitions RAG from a theoretical prototype into a robust, production-ready AI engineering system. By modularizing the backend via **FastAPI**, strictly typing inputs with **Pydantic**, orchestrating self-corrective logic via **LangGraph**, improving retrieval with **Cross-Encoders**, and wrapping it all in reproducible **Docker** containers, this assistant perfectly reflects practical, enterprise-grade LLM product development.
