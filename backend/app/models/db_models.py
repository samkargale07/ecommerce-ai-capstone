"""
SQLAlchemy ORM models — these map Python classes to the MySQL tables
we already created in Day 2 (sql/schema.sql) and Day 3 (sql/analytics_schema.sql).

We're NOT recreating tables here (no Base.metadata.create_all) — these
models just describe the existing tables so we can query them with the ORM.
"""
from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, ForeignKey
from app.database import Base


class Category(Base):
    __tablename__ = "category_translation"
    product_category_name = Column(String(100), primary_key=True)
    product_category_name_english = Column(String(100))


class Product(Base):
    __tablename__ = "products"
    product_id = Column(String(64), primary_key=True)
    product_category_name = Column(String(100), ForeignKey("category_translation.product_category_name"))
    product_name_length = Column(Integer)
    product_description_length = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Integer)
    product_length_cm = Column(Integer)
    product_height_cm = Column(Integer)
    product_width_cm = Column(Integer)


class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String(64), primary_key=True)
    customer_unique_id = Column(String(64))
    customer_zip_code_prefix = Column(String(10))
    customer_city = Column(String(100))
    customer_state = Column(String(10))


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id"))
    order_status = Column(String(30))
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)


class OrderItem(Base):
    __tablename__ = "order_items"
    order_id = Column(String(64), ForeignKey("orders.order_id"), primary_key=True)
    order_item_id = Column(Integer, primary_key=True)
    product_id = Column(String(64), ForeignKey("products.product_id"))
    seller_id = Column(String(64))
    shipping_limit_date = Column(DateTime)
    price = Column(DECIMAL(10, 2))
    freight_value = Column(DECIMAL(10, 2))


# ---------------------------------------------------------
# Analytics tables (Day 3)
# ---------------------------------------------------------
class CategorySalesAnalytics(Base):
    __tablename__ = "analytics_category_sales"
    product_category_name = Column(String(100), primary_key=True)
    total_orders = Column(Integer)
    total_revenue = Column(DECIMAL(14, 2))
    avg_order_value = Column(DECIMAL(10, 2))


class MonthlyTrendsAnalytics(Base):
    __tablename__ = "analytics_monthly_trends"
    sales_month = Column(String(7), primary_key=True)
    total_orders = Column(Integer)
    total_revenue = Column(DECIMAL(14, 2))


class TopProductsAnalytics(Base):
    __tablename__ = "analytics_top_products"
    product_id = Column(String(64), primary_key=True)
    product_category_name = Column(String(100))
    total_quantity_sold = Column(Integer)
    total_revenue = Column(DECIMAL(14, 2))


class ReviewSentimentAnalytics(Base):
    __tablename__ = "analytics_review_sentiment"
    product_category_name = Column(String(100), primary_key=True)
    avg_review_score = Column(DECIMAL(3, 2))
    total_reviews = Column(Integer)
