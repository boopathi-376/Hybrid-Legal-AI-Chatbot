from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RetrievalResult(BaseModel):
    content: str
    score: float
    page: Optional[int] = None

class ChatResponse(BaseModel):
    query: str
    answer: str
    thought: Optional[str] = None
    retrieved_context: Optional[List[RetrievalResult]] = None
    confidence: Optional[str] = None
