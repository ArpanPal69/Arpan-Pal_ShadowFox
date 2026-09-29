import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer, CrossEncoder
from schemas import RetrievedChunk, DocumentMetadata

# Initialize embedding model and reranker
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
document_store = [] # Store dicts with text and metadata

def add_documents(chunks: List[Dict]):
    global index, document_store
    if not chunks:
        return
    
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_model.encode(texts)
    
    index.add(np.array(embeddings).astype('float32'))
    document_store.extend(chunks)

def get_relevant_documents(query: str, top_k: int = 5, doc_filter: List[str] = None) -> List[RetrievedChunk]:
    if index.ntotal == 0:
        return []
        
    query_emb = embedding_model.encode([query])
    # Fetch 2x top_k to give reranker more options
    distances, indices = index.search(np.array(query_emb).astype('float32'), min(top_k * 3, index.ntotal))
    
    retrieved = []
    for i in indices[0]:
        if i != -1 and i < len(document_store):
            doc = document_store[i]
            if doc_filter:
                if doc['metadata']['source'] not in doc_filter:
                    continue
            retrieved.append(doc)
            
    if not retrieved:
        return []
        
    # Reranking using Cross-Encoder
    pairs = [[query, doc['text']] for doc in retrieved]
    scores = cross_encoder.predict(pairs)
    
    scored_docs = []
    for doc, score in zip(retrieved, scores):
        scored_docs.append((doc, score))
        
    # Sort by relevance score descending
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    final_docs = []
    for doc, score in scored_docs[:top_k]:
        final_docs.append(RetrievedChunk(
            text=doc['text'],
            metadata=DocumentMetadata(**doc['metadata']),
            relevance_score=float(score)
        ))
        
    return final_docs
