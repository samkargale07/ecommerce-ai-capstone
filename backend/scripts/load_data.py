"""
Loads the Olist CSV dataset into MySQL, following the schema in sql/schema.sql.

Run this AFTER:
  1. Creating the database (CREATE DATABASE ecommerce_capstone;)
  2. Running schema.sql to create the tables
  3. Placing all Olist CSVs into backend/data/

Usage (from backend/ folder, with venv activated):
    python scripts/load_data.py
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

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {filename} in backend/data/. "
            f"Download the Olist dataset from Kaggle and extract it there."
        )
    return pd.read_csv(path)


def to_sql_safe(df, table_name, chunksize=1000):
    """Insert a dataframe into MySQL, replacing NaN with None."""
    df = df.where(pd.notnull(df), None)
    df.to_sql(table_name, con=engine, if_exists="append", index=False, chunksize=chunksize, method="multi")
    print(f"  -> Loaded {len(df):,} rows into '{table_name}'")


def main():
    print("Starting data load...\n")

    # ---------------------------------------------------------
    # 1. Category translation (load first — products references it)
    # ---------------------------------------------------------
    print("[1/8] category_translation")
    cat_trans = load_csv("product_category_name_translation.csv")

    # Also pull in any category names that appear in products.csv but
    # are missing from the translation file, so the FK constraint doesn't break.
    products_raw = load_csv("olist_products_dataset.csv")
    all_categories = set(products_raw["product_category_name"].dropna().unique())
    known_categories = set(cat_trans["product_category_name"].dropna().unique())
    missing = all_categories - known_categories
    if missing:
        missing_df = pd.DataFrame({
            "product_category_name": list(missing),
            "product_category_name_english": None
        })
        cat_trans = pd.concat([cat_trans, missing_df], ignore_index=True)

    to_sql_safe(cat_trans, "category_translation")

    # ---------------------------------------------------------
    # 2. Customers
    # ---------------------------------------------------------
    print("[2/8] customers")
    customers = load_csv("olist_customers_dataset.csv")
    to_sql_safe(customers, "customers")

    # ---------------------------------------------------------
    # 3. Sellers
    # ---------------------------------------------------------
    print("[3/8] sellers")
    sellers = load_csv("olist_sellers_dataset.csv")
    to_sql_safe(sellers, "sellers")

    # ---------------------------------------------------------
    # 4. Products
    # ---------------------------------------------------------
    print("[4/8] products")
    products_raw = products_raw.rename(columns={
    "product_name_lenght": "product_name_length",
    "product_description_lenght": "product_description_length",
    })
    to_sql_safe(products_raw, "products")

    # ---------------------------------------------------------
    # 5. Orders
    # ---------------------------------------------------------
    print("[5/8] orders")
    orders = load_csv("olist_orders_dataset.csv")
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")
    to_sql_safe(orders, "orders")

    # ---------------------------------------------------------
    # 6. Order items
    # ---------------------------------------------------------
    print("[6/8] order_items")
    order_items = load_csv("olist_order_items_dataset.csv")
    order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"], errors="coerce")
    to_sql_safe(order_items, "order_items")

    # ---------------------------------------------------------
    # 7. Order payments
    # ---------------------------------------------------------
    print("[7/8] order_payments")
    payments = load_csv("olist_order_payments_dataset.csv")
    to_sql_safe(payments, "order_payments")

    # ---------------------------------------------------------
    # 8. Order reviews
    # ---------------------------------------------------------
    print("[8/8] order_reviews")
    reviews = load_csv("olist_order_reviews_dataset.csv")
    for col in ["review_creation_date", "review_answer_timestamp"]:
        reviews[col] = pd.to_datetime(reviews[col], errors="coerce")
    # Some duplicate (review_id, order_id) pairs exist in the raw data — drop them
    reviews = reviews.drop_duplicates(subset=["review_id", "order_id"])
    to_sql_safe(reviews, "order_reviews")

    print("\nAll tables loaded successfully.")


if __name__ == "__main__":
    main()
