"""
Day 6 — DL Embeddings

Generates a sentence embedding for each product category (using its
English translation) with a pretrained sentence-transformer model,
and stores the resulting vectors in the category_embeddings table.

Why category-level, not product-level: the Olist dataset only gives us
category names, not rich per-product descriptions. Embedding at the
category level gives us genuinely useful semantic search (matching a
free-text query to the closest category), without pretending we have
richer text data than we actually do.

Run this AFTER sql/embeddings_schema.sql has been executed.

Usage (from backend/ folder, with venv activated):
    python scripts/build_embeddings.py
"""
import os
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
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

# Small, fast, well-regarded general-purpose embedding model (~80MB download,
# runs fine on CPU — no GPU needed for a dataset this small).
MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    print(f"Loading sentence-transformer model '{MODEL_NAME}'... (first run downloads it, ~80MB)")
    model = SentenceTransformer(MODEL_NAME)

    print("Loading categories from database...")
    categories = pd.read_sql("SELECT * FROM category_translation", engine)

    # Use the English translation when available; fall back to the raw
    # Portuguese name (with underscores replaced by spaces) otherwise.
    def get_text(row):
        if pd.notna(row["product_category_name_english"]):
            return row["product_category_name_english"].replace("_", " ")
        return row["product_category_name"].replace("_", " ")

    categories["embedding_text"] = categories.apply(get_text, axis=1)

    print(f"Generating embeddings for {len(categories)} categories...")
    embeddings = model.encode(categories["embedding_text"].tolist(), show_progress_bar=True)

    print("Saving embeddings to database...")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM category_embeddings"))

    rows = []
    for i, row in categories.iterrows():
        rows.append({
            "product_category_name": row["product_category_name"],
            "product_category_name_english": row["product_category_name_english"],
            "embedding_json": json.dumps(embeddings[i].tolist()),
        })

    pd.DataFrame(rows).to_sql(
        "category_embeddings", con=engine, if_exists="append", index=False, method="multi"
    )
    print(f"Saved {len(rows)} category embeddings.")


if __name__ == "__main__":
    main()
