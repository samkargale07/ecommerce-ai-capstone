from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.genai_service import answer_question

router = APIRouter()


@router.get("/")
def chat(
    q: str = Query(..., min_length=1, description="Ask a natural language shopping question"),
    db: Session = Depends(get_db),
):
    """
    RAG-powered shopping assistant. Retrieves real product/category context
    relevant to the question, then asks Claude to answer using only that context.
    """
    return answer_question(q, db)
