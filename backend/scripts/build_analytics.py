"""
Day 3 — Big Data Aggregation

Reads raw relational data from MySQL into Pandas, computes several
business-relevant aggregations, and writes the results back into
dedicated analytics_* tables.

Run this AFTER:
  1. Day 2 is complete (raw tables populated)
  2. sql/analytics_schema.sql has been run to create the analytics tables

Usage (from backend/ folder, with venv activated):
    python scripts/build_analytics.py
"""
import os
import pandas as pd
from sqlalchemy import create_engine
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


def save(df, table_name):
    df.to_sql(table_name, con=engine, if_exists="append", index=False, method="multi")
    print(f"  -> Wrote {len(df):,} rows to '{table_name}'")


def main():
    print("Loading raw tables into Pandas...\n")

    orders = pd.read_sql("SELECT * FROM orders", engine)
    order_items = pd.read_sql("SELECT * FROM order_items", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    customers = pd.read_sql("SELECT * FROM customers", engine)
    reviews = pd.read_sql("SELECT * FROM order_reviews", engine)

    # Only count orders that were actually delivered/valid (exclude cancelled)
    valid_orders = orders[orders["order_status"] != "canceled"]

    # Merge order_items with orders and products — this becomes our base
    # dataframe for most revenue-based aggregations.
    merged = order_items.merge(valid_orders[["order_id", "customer_id", "order_purchase_timestamp"]], on="order_id")
    merged = merged.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
    merged["item_revenue"] = merged["price"] + merged["freight_value"]

    # ---------------------------------------------------------
    # 1. Category sales
    # ---------------------------------------------------------
    print("[1/5] analytics_category_sales")
    category_sales = (
        merged.groupby("product_category_name")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("item_revenue", "sum"),
        )
        .reset_index()
    )
    category_sales["avg_order_value"] = (
        category_sales["total_revenue"] / category_sales["total_orders"]
    ).round(2)
    category_sales["total_revenue"] = category_sales["total_revenue"].round(2)
    category_sales = category_sales.dropna(subset=["product_category_name"])
    save(category_sales, "analytics_category_sales")

    # ---------------------------------------------------------
    # 2. Monthly trends
    # ---------------------------------------------------------
    print("[2/5] analytics_monthly_trends")
    merged["sales_month"] = pd.to_datetime(merged["order_purchase_timestamp"]).dt.strftime("%Y-%m")
    monthly = (
        merged.groupby("sales_month")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("item_revenue", "sum"),
        )
        .reset_index()
    )
    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    save(monthly, "analytics_monthly_trends")

    # ---------------------------------------------------------
    # 3. Top products
    # ---------------------------------------------------------
    print("[3/5] analytics_top_products")
    top_products = (
        merged.groupby(["product_id", "product_category_name"])
        .agg(
            total_quantity_sold=("order_item_id", "count"),
            total_revenue=("item_revenue", "sum"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(200)  # keep top 200 — plenty for a dashboard, keeps table small
    )
    top_products["total_revenue"] = top_products["total_revenue"].round(2)
    save(top_products, "analytics_top_products")

    # ---------------------------------------------------------
    # 4. Review sentiment by category
    # ---------------------------------------------------------
    print("[4/5] analytics_review_sentiment")
    reviews_with_category = reviews.merge(
        order_items[["order_id", "product_id"]].drop_duplicates(subset=["order_id"]),
        on="order_id", how="left"
    ).merge(products[["product_id", "product_category_name"]], on="product_id", how="left")

    sentiment = (
        reviews_with_category.groupby("product_category_name")
        .agg(
            avg_review_score=("review_score", "mean"),
            total_reviews=("review_score", "count"),
        )
        .reset_index()
        .dropna(subset=["product_category_name"])
    )
    sentiment["avg_review_score"] = sentiment["avg_review_score"].round(2)
    save(sentiment, "analytics_review_sentiment")

    # ---------------------------------------------------------
    # 5. Sales by customer state
    # ---------------------------------------------------------
    print("[5/5] analytics_state_sales")
    merged_state = merged.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
    state_sales = (
        merged_state.groupby("customer_state")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("item_revenue", "sum"),
        )
        .reset_index()
        .dropna(subset=["customer_state"])
    )
    state_sales["total_revenue"] = state_sales["total_revenue"].round(2)
    save(state_sales, "analytics_state_sales")

    print("\nAll analytics tables built successfully.")


if __name__ == "__main__":
    main()
