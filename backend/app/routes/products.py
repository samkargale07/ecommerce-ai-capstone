from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.db_models import Product, Category, Recommendation
from app.models.schemas import ProductOut, CategoryOut, RecommendationOut
from app.services.embedding_service import search_categories

router = APIRouter()


def get_category_translation_map(db: Session) -> dict:
    """
    Returns {portuguese_category_name: english_category_name}.
    Used to attach a readable English label to every product response,
    since the raw catalog data (Olist) only stores Portuguese category slugs.
    """
    rows = db.query(Category).all()
    return {row.product_category_name: row.product_category_name_english for row in rows}


def attach_english_name(product: Product, category_map: dict) -> dict:
    """Converts a Product ORM object into a dict with the English category name attached."""
    return {
        "product_id": product.product_id,
        "product_category_name": product.product_category_name,
        "product_category_name_english": category_map.get(product.product_category_name),
        "product_weight_g": product.product_weight_g,
        "product_length_cm": product.product_length_cm,
        "product_height_cm": product.product_height_cm,
        "product_width_cm": product.product_width_cm,
    }


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
    products = query.offset(offset).limit(limit).all()

    category_map = get_category_translation_map(db)
    return [attach_english_name(p, category_map) for p in products]


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
    """Simple keyword search over product category names."""
    products = (
        db.query(Product)
        .filter(Product.product_category_name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    category_map = get_category_translation_map(db)
    return [attach_english_name(p, category_map) for p in products]


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
    category_map = get_category_translation_map(db)
    return [attach_english_name(p, category_map) for p in products]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get a single product by its ID."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category_map = get_category_translation_map(db)
    return attach_english_name(product, category_map)


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