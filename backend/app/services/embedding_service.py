"""
Embedding service — loads the sentence-transformer model once (expensive
to load, so we do it a single time at import) and provides a function to
semantically search categories given a free-text query.
"""
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import text

MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once when this module is first imported (i.e. once per server run,
# not once per request) — this is the expensive step we don't want repeated.
_model = None


def get_model():
    global _model
    if _model is None:
        print("Loading sentence-transformer model for semantic search...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search_categories(query: str, db: Session, top_k: int = 3):
    """
    Embeds the query text, compares it against all stored category
    embeddings, and returns the top_k most semantically similar categories.

    Returns: list of dicts with product_category_name, product_category_name_english, score
    """
    model = get_model()
    query_vector = model.encode(query)

    rows = db.execute(
        text("SELECT product_category_name, product_category_name_english, embedding_json FROM category_embeddings")
    ).fetchall()

    results = []
    for row in rows:
        category_vector = np.array(json.loads(row.embedding_json))
        score = cosine_similarity(query_vector, category_vector)
        results.append({
            "product_category_name": row.product_category_name,
            "product_category_name_english": row.product_category_name_english,
            "score": round(score, 4),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
