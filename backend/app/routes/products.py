from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.db_models import Product, Category
from app.models.schemas import ProductOut, CategoryOut

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
    """Simple keyword search over product category names."""
    results = (
        db.query(Product)
        .filter(Product.product_category_name.ilike(f"%{q}%"))
        .limit(limit)
        .all()
    )
    return results


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get a single product by its ID."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product