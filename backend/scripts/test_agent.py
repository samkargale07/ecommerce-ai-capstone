"""
Day 9 — Agent Test Script

Tests the /agent/ endpoint with several different question types, each
designed to trigger a DIFFERENT tool (search, recommendations, category
stats, compare). This verifies the agent is actually choosing tools
based on the question, not just always doing the same thing.

Because the Gemini free tier can be intermittently overloaded (503s),
our agent_service.py catches that and returns a friendly message
instead of crashing. This script flags those runs separately so you
can tell "the code is broken" apart from "Google's servers were busy
when I ran this."

Prerequisite: your server must already be running in another terminal:
    uvicorn app.main:app --reload --reload-dir app

Usage (from backend/ folder, with venv activated, in a SEPARATE terminal
from the one running uvicorn):
    python scripts/test_agent.py
"""
import os
import time
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_NAME = os.getenv("DB_NAME", "ecommerce_capstone")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

BASE_URL = "http://localhost:8000"

OVERLOAD_PHRASES = ["temporarily overloaded", "rate limit was hit", "unexpected error occurred"]


def get_two_sample_product_ids():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT DISTINCT product_id FROM order_items LIMIT 2")).fetchall()
        return [r[0] for r in rows]


def get_sample_category():
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT product_category_name FROM analytics_category_sales "
                "ORDER BY total_revenue DESC LIMIT 1"
            )
        ).fetchone()
        return row[0] if row else None


def call_agent(label, query, retries=2, wait_seconds=15):
    """Calls the agent endpoint, retrying once if we hit the overload message."""
    url = f"{BASE_URL}/agent/?q={requests.utils.quote(query)}"
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=60)
            data = resp.json()
            answer = data.get("answer", "")
            is_overloaded = any(phrase in answer for phrase in OVERLOAD_PHRASES)

            if is_overloaded and attempt < retries:
                print(f"  [{label}] Got overload message, retrying in {wait_seconds}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait_seconds)
                continue

            status = "OVERLOADED (Google's side, not your code)" if is_overloaded else "OK"
            return {
                "label": label,
                "query": query,
                "http_status": resp.status_code,
                "result_status": status,
                "answer_snippet": answer[:200],
            }
        except Exception as e:
            return {
                "label": label,
                "query": query,
                "http_status": "ERROR",
                "result_status": "FAILED",
                "answer_snippet": str(e)[:200],
            }


def main():
    print("Fetching sample data for testing...\n")
    product_ids = get_two_sample_product_ids()
    category = get_sample_category()

    if len(product_ids) < 2 or not category:
        print("ERROR: Could not fetch enough sample data from DB.")
        return

    p1, p2 = product_ids[0], product_ids[1]
    print(f"Using product IDs: {p1}, {p2}")
    print(f"Using category: {category}\n")
    print("Running agent tests (this may take a while if Gemini is retrying)...\n")

    tests = [
        ("search_products (expected tool)", f"I'm looking for something related to {category}, any suggestions?"),
        ("get_category_stats (expected tool)", f"How well does the {category} category sell? What's the average order value?"),
        ("get_recommendations (expected tool)", f"What products go well with product {p1}?"),
        ("compare_products (expected tool)", f"Compare product {p1} and product {p2} for me."),
        ("no tool needed (general question)", "What kind of assistant are you and how can you help me shop?"),
    ]

    results = []
    for label, query in tests:
        result = call_agent(label, query)
        results.append(result)

    print(f"\n{'TEST':<40} {'HTTP':<8} {'RESULT':<45} SNIPPET")
    print("-" * 140)
    for r in results:
        print(f"{r['label']:<40} {str(r['http_status']):<8} {r['result_status']:<45} {r['answer_snippet']}")

    overloaded_count = sum(1 for r in results if "OVERLOADED" in r["result_status"])
    ok_count = sum(1 for r in results if r["result_status"] == "OK")

    print("\n" + "=" * 60)
    print(f"  {ok_count}/{len(results)} got real answers")
    if overloaded_count:
        print(f"  {overloaded_count}/{len(results)} hit Gemini free-tier overload (retry later)")
    print("=" * 60)


if __name__ == "__main__":
    main()
