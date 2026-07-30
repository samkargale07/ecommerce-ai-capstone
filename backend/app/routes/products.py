from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.database import get_db
from app.models.db_models import Product, Category, Recommendation
from app.models.schemas import ProductOut, CategoryOut, RecommendationOut
from app.services.embedding_service import search_categories

router = APIRouter()


@router.get("/", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = Query(None, description="Filter by product_category_name"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List products, optionally filtered by category, with pagination."""
    query = db.query(Product)
    if category:
        query = query.filter(Product.product_category_name == category)
    return query.offset(offset).limit(limit).all()


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all product categories with their English translation."""
    return db.query(Category).all()


@router.get("/search", response_model=List[ProductOut])
def search_products(
    q: str = Query(..., min_length=1, description="Search term (matches category name)"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """
    Simple keyword search over product category names.
    (Day 6 will add real semantic search using embeddings —
    this is the basic keyword version for now.)
    """
    results = (
        db.query(Product)
        .filter(Product.product_category_name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    return results


@router.get("/semantic-search", response_model=List[ProductOut])
def semantic_search(
    q: str = Query(..., min_length=1, description="Natural language search query, e.g. 'gift for outdoor fitness'"),
    top_categories: int = Query(2, le=5, description="How many matching categories to pull products from"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """
    DL-powered semantic search: embeds the query text and matches it
    against category embeddings by meaning, not just keyword overlap.
    Then returns products from the best-matching categories.
    """
    matched_categories = search_categories(q, db, top_k=top_categories)
    category_names = [c["product_category_name"] for c in matched_categories]

    if not category_names:
        return []

    products = (
        db.query(Product)
        .filter(Product.product_category_name.in_(category_names))
        .limit(limit)
        .all()
    )
    return products


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get a single product by its ID."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}/recommendations", response_model=List[RecommendationOut])
def get_recommendations(
    product_id: str,
    method: Optional[str] = Query(
        None, description="Filter by method: 'collaborative' or 'content'. Omit for both."
    ),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """
    Get recommended products for a given product_id.
    - method='collaborative': based on co-purchase patterns
    - method='content': based on category/attribute similarity
    - omitted: returns both, sorted by score
    """
    query = db.query(Recommendation).filter(Recommendation.product_id == product_id)
    if method:
        query = query.filter(Recommendation.method == method)
    return query.order_by(Recommendation.score.desc()).limit(limit).all()
