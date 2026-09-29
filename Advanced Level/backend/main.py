from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from schemas import QueryRequest, QueryResponse
from document_loader import process_document
import faiss_retriever
from agent import rag_app
from config import UPLOAD_DIR, OPENAI_API_KEY
import os
import shutil

app = FastAPI(title="Production-Style Agentic RAG API", description="Advanced multi-stage RAG API with self-correction")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt', '.md')):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        chunks = process_document(file_path, file.filename)
        faiss_retriever.add_documents(chunks)
        return {"message": f"Successfully processed {file.filename}. Added {len(chunks)} chunks to vector store."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_system(req: QueryRequest, x_api_key: str = Header(None)):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    api_key = x_api_key or OPENAI_API_KEY
    if not api_key:
        raise HTTPException(status_code=401, detail="OpenAI API Key is missing. Provide it in frontend or environment.")
        
    initial_state = {
        "question": req.query,
        "original_question": req.query,
        "documents": [],
        "answer": "",
        "loop_count": 0,
        "steps": ["User submitted query."],
        "document_ids": req.document_ids,
        "api_key": api_key
    }
    
    try:
        final_state = rag_app.invoke(initial_state)
        
        answer = final_state.get("answer", "")
        if not answer or answer == "HALLUCINATION_DETECTED":
            answer = "I could not find an answer grounded in the documents provided or max retries exceeded."
            final_state["steps"].append("Failed to find a grounded answer within limits.")
            
        return QueryResponse(
            answer=answer,
            citations=final_state.get("documents", []),
            agent_steps=final_state.get("steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RAG pipeline: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
