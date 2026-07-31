"""
GenAI Service — Retrieval-Augmented Generation (RAG)

Given a natural-language question, this:
1. RETRIEVES relevant context from our own data (semantic category search
   + real product listings + category sales stats)
2. AUGMENTS a prompt to Gemini with that real, grounded context
3. GENERATES a natural-language answer based on it

Uses Google's Gemini API (free tier — no credit card needed), via the
official `google-genai` SDK.

This is deliberately simple/single-turn — Day 9's Agentic AI layer will
build on top of this with multi-step reasoning and tool selection.
"""
import os
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

from app.services.embedding_service import search_categories

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash"  # strong quality, generous free tier

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def retrieve_context(query: str, db: Session, top_categories: int = 2, products_per_category: int = 5) -> str:
    """
    Pulls together real data relevant to the query:
    - Best-matching categories (via Day 6 semantic search)
    - A few real products from those categories
    - Sales/popularity stats for those categories (Day 3 analytics)
    """
    matched = search_categories(query, db, top_k=top_categories)
    if not matched:
        return "No relevant product categories found in the catalog."

    context_parts = []
    for cat in matched:
        cat_name = cat["product_category_name"]
        cat_english = cat["product_category_name_english"] or cat_name

        products = db.execute(
            text(
                "SELECT product_id, product_weight_g, product_length_cm, "
                "product_height_cm, product_width_cm FROM products "
                "WHERE product_category_name = :cat LIMIT :lim"
            ),
            {"cat": cat_name, "lim": products_per_category},
        ).fetchall()

        stats = db.execute(
            text(
                "SELECT total_orders, total_revenue, avg_order_value "
                "FROM analytics_category_sales WHERE product_category_name = :cat"
            ),
            {"cat": cat_name},
        ).fetchone()

        section = f"\nCategory: {cat_english} (match relevance: {cat['score']})\n"
        if stats:
            section += (
                f"  - Popularity: {stats.total_orders} orders, "
                f"avg order value ${stats.avg_order_value}\n"
            )
        section += f"  - Sample products in this category ({len(products)} shown):\n"
        for p in products:
            section += (
                f"    - Product ID {p.product_id}: "
                f"weight {p.product_weight_g}g, "
                f"dimensions {p.product_length_cm}x{p.product_height_cm}x{p.product_width_cm}cm\n"
            )
        context_parts.append(section)

    return "\n".join(context_parts)


def generate_answer(query: str, context: str) -> str:
    """Sends the query + retrieved context to Gemini and returns its answer."""
    if not client:
        return (
            "GenAI is not configured — GEMINI_API_KEY is missing from .env. "
            "Get a free key from aistudio.google.com and add it to enable this feature."
        )

    system_prompt = (
        "You are a helpful shopping assistant for an e-commerce platform. "
        "Answer the customer's question using ONLY the product context provided below. "
        "Be concise and friendly. If the context doesn't fully answer the question, "
        "say so honestly rather than making up details. Mention specific product IDs "
        "when recommending something, so the customer can look them up.\n\n"
        f"PRODUCT CONTEXT:\n{context}"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    return response.text


def answer_question(query: str, db: Session) -> dict:
    """Full RAG pipeline: retrieve + generate. Returns both the answer and the context used (for transparency/debugging)."""
    context = retrieve_context(query, db)
    answer = generate_answer(query, context)
    return {"query": query, "context_used": context, "answer": answer}

