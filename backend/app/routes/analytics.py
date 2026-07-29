from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.db_models import (
    CategorySalesAnalytics,
    MonthlyTrendsAnalytics,
    TopProductsAnalytics,
)
from app.models.schemas import CategorySalesOut, MonthlyTrendOut, TopProductOut

router = APIRouter()


@router.get("/category-sales", response_model=List[CategorySalesOut])
def category_sales(db: Session = Depends(get_db)):
    """Revenue and order counts per product category."""
    return (
        db.query(CategorySalesAnalytics)
        .order_by(CategorySalesAnalytics.total_revenue.desc())
        .all()
    )


@router.get("/monthly-trends", response_model=List[MonthlyTrendOut])
def monthly_trends(db: Session = Depends(get_db)):
    """Order count and revenue per month — for time-series charts."""
    return (
        db.query(MonthlyTrendsAnalytics)
        .order_by(MonthlyTrendsAnalytics.sales_month.asc())
        .all()
    )


@router.get("/top-products", response_model=List[TopProductOut])
def top_products(limit: int = 20, db: Session = Depends(get_db)):
    """Best-selling products by revenue."""
    return (
        db.query(TopProductsAnalytics)
        .order_by(TopProductsAnalytics.total_revenue.desc())
        .limit(limit)
        .all()
    )