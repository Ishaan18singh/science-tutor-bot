import os
import sys
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))

from llm_router import get_tutor_response

router = APIRouter()


# ── Request/Response Schemas ──────────────────────────────
class ChatMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[ChatMessage]] = []

class SourceInfo(BaseModel):
    subject: str
    class_: str
    chapter: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


# ── Endpoint ───────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Convert Pydantic chat history into plain dicts for the LLM
    history = [{"role": m.role, "content": m.content} for m in request.chat_history]

    answer, chunks = get_tutor_response(request.question, history)

    sources = [
        {
            "subject": c["subject"],
            "class": c["class"],
            "chapter": c["chapter"],
            "score": float(c["score"])
        }
        for c in chunks
    ]

    return ChatResponse(answer=answer, sources=sources)