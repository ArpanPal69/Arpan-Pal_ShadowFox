import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from schemas import RetrievedChunk, DocumentMetadata

def process_document(file_path: str, filename: str) -> List[dict]:
    ext = os.path.splitext(file_path)[-1].lower()
    docs = []
    
    if ext == '.pdf':
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    elif ext == '.txt':
        loader = TextLoader(file_path)
        docs = loader.load()
    elif ext == '.md':
        loader = UnstructuredMarkdownLoader(file_path)
        docs = loader.load()
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(docs)
    
    formatted_chunks = []
    for chunk in chunks:
        page = chunk.metadata.get('page', None)
        if page is not None:
            page += 1 # 1-indexed for display purposes
        metadata = DocumentMetadata(source=filename, page=page)
        formatted_chunks.append({
            "text": chunk.page_content,
            "metadata": metadata.model_dump()
        })
        
    return formatted_chunks
