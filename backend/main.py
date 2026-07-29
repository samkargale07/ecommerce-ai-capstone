"""
Entry point for the E-commerce AI Capstone backend.
Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import products, analytics

app = FastAPI(
    title="E-commerce AI Assistant API",
    description="Capstone backend: SQL + Big Data + ML + DL + GenAI + Agentic AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "E-commerce AI Capstone API is running"}


app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])