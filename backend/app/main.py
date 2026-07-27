"""
Entry point for the E-commerce AI Capstone backend.
Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

app = FastAPI(
    title="E-commerce AI Assistant API",
    description="Capstone backend: SQL + Big Data + ML + DL + GenAI + Agentic AI",
    version="0.1.0",
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "E-commerce AI Capstone API is running"}


# Routers will be added here as we build them:
# from app.routes import products, recommendations, chat
# app.include_router(products.router, prefix="/products", tags=["products"])
