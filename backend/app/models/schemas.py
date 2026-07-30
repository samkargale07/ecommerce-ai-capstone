"""
Pydantic schemas — define the shape of JSON responses our API sends back.
These are separate from the SQLAlchemy models (db_models.py) on purpose:
ORM models describe database tables, schemas describe API contracts.
"""
from pydantic import BaseModel
from typing import Optional


class ProductOut(BaseModel):
    product_id: str
    product_category_name: Optional[str]
    product_weight_g: Optional[int]
    product_length_cm: Optional[int]
    product_height_cm: Optional[int]
    product_width_cm: Optional[int]

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    product_category_name: str
    product_category_name_english: Optional[str]

    class Config:
        from_attributes = True


class CategorySalesOut(BaseModel):
    product_category_name: str
    total_orders: int
    total_revenue: float
    avg_order_value: float

    class Config:
        from_attributes = True


class MonthlyTrendOut(BaseModel):
    sales_month: str
    total_orders: int
    total_revenue: float

    class Config:
        from_attributes = True


class TopProductOut(BaseModel):
    product_id: str
    product_category_name: Optional[str]
    total_quantity_sold: int
    total_revenue: float

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    recommended_product_id: str
    method: str
    score: float

    class Config:
        from_attributes = True
