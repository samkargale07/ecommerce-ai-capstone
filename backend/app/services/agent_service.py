"""
Agentic AI Service — Day 9

Unlike Day 8's fixed RAG pipeline (always: search -> retrieve -> generate),
this gives Gemini a set of real tools and lets IT decide which one(s) to
call, with what arguments, based on what the user actually asked.

Uses Gemini's automatic function calling (AFC): we hand it plain Python
functions with type hints + docstrings, and the SDK handles the full
loop — calling our functions, feeding results back to the model, and
returning a final grounded answer.

Each tool function opens its own short-lived DB session internally
(rather than receiving one as a parameter), because Gemini's function
calling only supplies arguments it can infer from the conversation —
it has no notion of a FastAPI request's `db` dependency.
"""
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.database import SessionLocal
from app.services.embedding_service import search_categories
from sqlalchemy import text

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# =========================================================
# TOOLS — plain Python functions the agent can call.
# The docstring IS the instruction the model reads to decide
# when/how to use each tool — keep them clear and specific.
# =========================================================

def search_products(query: str, limit: int = 5) -> str:
    """
    Search the product catalog using natural language (semantic search).
    Use this when the user describes what they want but doesn't give a
    specific product ID or category name.

    Args:
        query: A natural language description of what the user is looking for.
        limit: Maximum number of products to return (default 5).

    Returns:
        A text summary of matching products with their IDs, category, weight, and dimensions.
    """
    db = SessionLocal()
    try:
        matched = search_categories(query, db, top_k=2)
        if not matched:
            return "No matching categories found."

        results = []
        for cat in matched:
            products = db.execute(
                text(
                    "SELECT product_id, product_weight_g, product_length_cm, "
                    "product_height_cm, product_width_cm FROM products "
                    "WHERE product_category_name = :cat LIMIT :lim"
                ),
                {"cat": cat["product_category_name"], "lim": limit},
            ).fetchall()
            for p in products:
                results.append(
                    f"Product ID {p.product_id} (category: {cat['product_category_name_english']}): "
                    f"weight {p.product_weight_g}g, dimensions {p.product_length_cm}x{p.product_height_cm}x{p.product_width_cm}cm"
                )
        return "\n".join(results) if results else "No products found."
    finally:
        db.close()


def get_recommendations(product_id: str, limit: int = 5) -> str:
    """
    Get recommended products similar to a given product, based on
    co-purchase patterns (collaborative filtering) and attribute
    similarity (content-based filtering). Use this when the user
    already has a specific product ID and wants similar/related items.

    Args:
        product_id: The exact product ID to get recommendations for.
        limit: Maximum number of recommendations to return (default 5).

    Returns:
        A text summary of recommended product IDs with their similarity method and score.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                "SELECT recommended_product_id, method, score FROM recommendations "
                "WHERE product_id = :pid ORDER BY score DESC LIMIT :lim"
            ),
            {"pid": product_id, "lim": limit},
        ).fetchall()
        if not rows:
            return f"No recommendations found for product {product_id}. It may not have enough purchase/attribute data."
        return "\n".join(
            f"Recommended: {r.recommended_product_id} (method: {r.method}, score: {r.score})"
            for r in rows
        )
    finally:
        db.close()


def get_category_stats(category_name: str) -> str:
    """
    Get sales analytics for a product category: total orders, total
    revenue, and average order value. Use this when the user asks
    about popularity, sales, or trends for a category.

    Args:
        category_name: The category name (in Portuguese, as stored in the catalog,
            e.g. 'beleza_saude', 'esporte_lazer'). If unsure of the exact name,
            use search_products first to find the right category.

    Returns:
        A text summary of the category's sales performance, or a not-found message.
    """
    db = SessionLocal()
    try:
        row = db.execute(
            text(
                "SELECT total_orders, total_revenue, avg_order_value FROM analytics_category_sales "
                "WHERE product_category_name = :cat"
            ),
            {"cat": category_name},
        ).fetchone()
        if not row:
            return f"No analytics found for category '{category_name}'."
        return (
            f"Category '{category_name}': {row.total_orders} total orders, "
            f"${row.total_revenue} total revenue, ${row.avg_order_value} average order value."
        )
    finally:
        db.close()


def compare_products(product_id_1: str, product_id_2: str) -> str:
    """
    Compare two specific products side-by-side by weight and dimensions.
    Use this when the user explicitly wants to compare two known product IDs.

    Args:
        product_id_1: The first product ID.
        product_id_2: The second product ID.

    Returns:
        A text comparison of both products' attributes.
    """
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                "SELECT product_id, product_category_name, product_weight_g, "
                "product_length_cm, product_height_cm, product_width_cm FROM products "
                "WHERE product_id IN (:p1, :p2)"
            ),
            {"p1": product_id_1, "p2": product_id_2},
        ).fetchall()
        if len(rows) < 2:
            return "One or both product IDs were not found in the catalog."
        lines = []
        for p in rows:
            lines.append(
                f"{p.product_id} — category: {p.product_category_name}, "
                f"weight: {p.product_weight_g}g, dimensions: {p.product_length_cm}x{p.product_height_cm}x{p.product_width_cm}cm"
            )
        return "\n".join(lines)
    finally:
        db.close()


# =========================================================
# AGENT — hands the tools to Gemini and lets it decide
# =========================================================

AGENT_SYSTEM_PROMPT = (
    "You are a shopping assistant agent for an e-commerce platform. You have "
    "tools available to search products, get recommendations, check category "
    "sales stats, and compare products. Decide which tool(s) to use based on "
    "what the user is asking — don't call tools you don't need. Always ground "
    "your final answer in the actual tool results; never invent product IDs, "
    "prices, or stats. If a tool returns no results, say so honestly. Be "
    "concise and friendly."
)


def run_agent(query: str) -> dict:
    """
    Sends the user's query to Gemini along with the available tools.
    Gemini automatically calls whichever tools it decides are needed
    (possibly multiple, possibly none) and returns a final answer.
    """
    if not client:
        return {
            "query": query,
            "answer": "GenAI is not configured — GEMINI_API_KEY is missing from .env.",
            "tools_available": [],
        }

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=AGENT_SYSTEM_PROMPT,
                tools=[search_products, get_recommendations, get_category_stats, compare_products],
                max_output_tokens=2048,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        answer_text = response.text
    except Exception as e:
        error_str = str(e)
        if "503" in error_str or "UNAVAILABLE" in error_str or "high demand" in error_str.lower():
            answer_text = (
                "The AI service is temporarily overloaded (this is common on free tiers "
                "during peak times). Please wait a moment and try again."
            )
        elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            answer_text = (
                "The free tier's rate limit was hit for this API key. Please wait a "
                "minute before trying again."
            )
        else:
            answer_text = f"An unexpected error occurred while contacting the AI service: {error_str}"

    return {
        "query": query,
        "answer": answer_text,
        "tools_available": [
            "search_products", "get_recommendations", "get_category_stats", "compare_products"
        ],
    }
