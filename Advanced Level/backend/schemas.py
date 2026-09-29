from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentMetadata(BaseModel):
    source: str
    page: Optional[int] = None

class RetrievedChunk(BaseModel):
    text: str
    metadata: DocumentMetadata
    relevance_score: float = 0.0

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="The user's question.")
    document_ids: Optional[List[str]] = Field(default=None, description="Scope search to specific docs.")

class QueryResponse(BaseModel):
    answer: str
    citations: List[RetrievedChunk]
    agent_steps: List[str]
