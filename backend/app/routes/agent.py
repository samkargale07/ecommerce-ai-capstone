from fastapi import APIRouter, Query

from app.services.agent_service import run_agent

router = APIRouter()


@router.get("/")
def agent_chat(
    q: str = Query(..., min_length=1, description="Ask the shopping agent anything"),
):
    """
    Agentic AI shopping assistant. Unlike /chat (fixed RAG pipeline),
    this gives Gemini real tools (search, recommendations, category
    stats, compare) and lets it decide which to use based on the question.
    """
    return run_agent(q)
