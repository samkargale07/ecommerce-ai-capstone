"""
Day 5 — ML Recommender

Builds two types of product recommendations and stores them in the
`recommendations` table:

1. COLLABORATIVE FILTERING (co-purchase based)
   "Products frequently bought together in the same order."
   We use this instead of classic user-based CF because most Olist
   customers only order once — there's not enough repeat-customer
   signal for traditional user-based collaborative filtering.

2. CONTENT-BASED FILTERING
   "Products similar in category, weight, and dimensions."
   Uses cosine similarity over a feature vector per product.

Run this AFTER Day 2 (raw tables) and Day 4 (recommendations_schema.sql) are done.

Usage (from backend/ folder, with venv activated):
    python scripts/build_recommendations.py
"""
import os
from collections import defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
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

TOP_N = 10  # how many recommendations to store per product, per method


def clear_recommendations():
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM recommendations"))
    print("Cleared existing recommendations table.\n")


def save_recommendations(rows):
    """rows: list of dicts with keys product_id, recommended_product_id, method, score"""
    if not rows:
        return
    df = pd.DataFrame(rows)
    df.to_sql("recommendations", con=engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"  -> Wrote {len(df):,} rows")


# =========================================================
# METHOD 1: Collaborative filtering (co-purchase)
# =========================================================
def build_collaborative_recommendations(order_items):
    print("[1/2] Building collaborative (co-purchase) recommendations...")

    # Group product_ids by order — only orders with 2+ distinct products matter
    baskets = order_items.groupby("order_id")["product_id"].apply(lambda x: list(set(x)))
    baskets = baskets[baskets.apply(len) >= 2]
    print(f"  Found {len(baskets):,} multi-item orders to analyze co-purchases from")

    co_counts = defaultdict(lambda: defaultdict(int))
    for products in baskets:
        for a, b in combinations(sorted(products), 2):
            co_counts[a][b] += 1
            co_counts[b][a] += 1

    rows = []
    for product_id, related in co_counts.items():
        # Sort related products by co-purchase count, descending
        top_related = sorted(related.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
        max_count = top_related[0][1] if top_related else 1
        for related_id, count in top_related:
            rows.append({
                "product_id": product_id,
                "recommended_product_id": related_id,
                "method": "collaborative",
                "score": round(count / max_count, 4),  # normalize 0-1 per product
            })

    save_recommendations(rows)
    print(f"  Covered {len(co_counts):,} products with collaborative recommendations\n")


# =========================================================
# METHOD 2: Content-based filtering (category + attributes)
# =========================================================
def build_content_recommendations(products):
    print("[2/2] Building content-based (similarity) recommendations...")

    # Drop products missing key numeric attributes — can't compare without them
    df = products.dropna(subset=["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]).copy()
    df = df.reset_index(drop=True)
    print(f"  Using {len(df):,} products with complete attribute data")

    # One-hot encode category
    category_dummies = pd.get_dummies(df["product_category_name"], prefix="cat")

    # Normalize numeric features so no single feature (e.g. weight in grams) dominates
    numeric_cols = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    scaler = StandardScaler()
    numeric_scaled = scaler.fit_transform(df[numeric_cols])

    feature_matrix = np.hstack([category_dummies.values, numeric_scaled])

    # Use NearestNeighbors instead of a full pairwise similarity matrix —
    # far more memory-efficient for ~30K products.
    n_neighbors = min(TOP_N + 1, len(df))  # +1 because a product is always its own nearest neighbor
    nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine", algorithm="brute")
    nn_model.fit(feature_matrix)

    distances, indices = nn_model.kneighbors(feature_matrix)

    rows = []
    product_ids = df["product_id"].values
    for i in range(len(df)):
        current_product = product_ids[i]
        for j in range(1, len(indices[i])):  # skip index 0 — it's the product itself
            neighbor_idx = indices[i][j]
            similarity_score = round(1 - distances[i][j], 4)  # cosine distance -> similarity
            rows.append({
                "product_id": current_product,
                "recommended_product_id": product_ids[neighbor_idx],
                "method": "content",
                "score": similarity_score,
            })

        # Write in batches of ~5000 rows to avoid holding everything in memory at once
        if len(rows) >= 5000:
            save_recommendations(rows)
            rows = []

    save_recommendations(rows)  # flush remaining
    print(f"  Covered {len(df):,} products with content-based recommendations\n")


def main():
    print("Loading data...\n")
    order_items = pd.read_sql("SELECT order_id, product_id FROM order_items", engine)
    products = pd.read_sql(
        "SELECT product_id, product_category_name, product_weight_g, "
        "product_length_cm, product_height_cm, product_width_cm FROM products",
        engine,
    )

    clear_recommendations()
    build_collaborative_recommendations(order_items)
    build_content_recommendations(products)

    print("All recommendations built successfully.")


if __name__ == "__main__":
    main()
