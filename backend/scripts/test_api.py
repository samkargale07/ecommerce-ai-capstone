"""
Day 7 — Full API Test Script

Hits every endpoint built so far (Days 4-6) against a running server
and reports PASS/FAIL for each, with a snippet of the response.

Prerequisite: your server must already be running in another terminal:
    uvicorn app.main:app --reload

Usage (from backend/ folder, with venv activated, in a SEPARATE terminal
from the one running uvicorn):
    python scripts/test_api.py
"""
import os
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

results = []


def check(name, method, path, expected_status=200):
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.get(url, timeout=15)
        passed = resp.status_code == expected_status
        snippet = str(resp.json())[:150] if resp.headers.get("content-type", "").startswith("application/json") else resp.text[:150]
        results.append((name, passed, resp.status_code, snippet))
    except Exception as e:
        results.append((name, False, "ERROR", str(e)[:150]))


def get_sample_product_id():
    with engine.connect() as conn:
        row = conn.execute(text("SELECT product_id FROM order_items LIMIT 1")).fetchone()
        return row[0] if row else None


def get_sample_category():
    with engine.connect() as conn:
        row = conn.execute(text("SELECT product_category_name FROM products WHERE product_category_name IS NOT NULL LIMIT 1")).fetchone()
        return row[0] if row else None


def main():
    print("Fetching sample data for testing...")
    sample_product_id = get_sample_product_id()
    sample_category = get_sample_category()

    if not sample_product_id or not sample_category:
        print("ERROR: Could not fetch sample product/category from DB. Is your data loaded?")
        return

    print(f"Using sample product_id: {sample_product_id}")
    print(f"Using sample category: {sample_category}\n")
    print("Running tests against", BASE_URL, "...\n")

    # --- Health check ---
    check("Health check", "GET", "/")

    # --- Products ---
    check("List products", "GET", "/products?limit=5")
    check("List products (filtered by category)", "GET", f"/products?category={sample_category}&limit=5")
    check("List categories", "GET", "/products/categories")
    check("Keyword search", "GET", "/products/search?q=moveis")
    check("Semantic search", "GET", "/products/semantic-search?q=outdoor fitness gear")
    check("Get single product", "GET", f"/products/{sample_product_id}")
    check("Get product recommendations (both methods)", "GET", f"/products/{sample_product_id}/recommendations")
    check("Get product recommendations (collaborative only)", "GET", f"/products/{sample_product_id}/recommendations?method=collaborative")
    check("Get product recommendations (content only)", "GET", f"/products/{sample_product_id}/recommendations?method=content")
    check("Get product (invalid ID -> expect 404)", "GET", "/products/this_id_does_not_exist", expected_status=404)

    # --- Analytics ---
    check("Category sales analytics", "GET", "/analytics/category-sales")
    check("Monthly trends analytics", "GET", "/analytics/monthly-trends")
    check("Top products analytics", "GET", "/analytics/top-products")

    # --- Print results ---
    print(f"{'TEST':<55} {'RESULT':<8} {'STATUS':<10} SNIPPET")
    print("-" * 120)
    pass_count = 0
    for name, passed, status, snippet in results:
        result_str = "PASS" if passed else "FAIL"
        if passed:
            pass_count += 1
        print(f"{name:<55} {result_str:<8} {str(status):<10} {snippet}")

    print("\n" + "=" * 50)
    print(f"  {pass_count}/{len(results)} tests passed")
    print("=" * 50)


if __name__ == "__main__":
    main()
