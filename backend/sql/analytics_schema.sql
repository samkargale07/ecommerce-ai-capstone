-- =========================================================
-- Analytics Tables — Day 3 Big Data Aggregation
-- These are pre-computed summary tables, refreshed by
-- scripts/build_analytics.py. The dashboard (Day 12) reads
-- from these instead of aggregating raw data every time.
-- =========================================================

DROP TABLE IF EXISTS analytics_category_sales;
DROP TABLE IF EXISTS analytics_monthly_trends;
DROP TABLE IF EXISTS analytics_top_products;
DROP TABLE IF EXISTS analytics_review_sentiment;
DROP TABLE IF EXISTS analytics_state_sales;

CREATE TABLE analytics_category_sales (
    product_category_name VARCHAR(100) PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(14,2),
    avg_order_value DECIMAL(10,2)
);

CREATE TABLE analytics_monthly_trends (
    sales_month VARCHAR(7) PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(14,2)
);

CREATE TABLE analytics_top_products (
    product_id VARCHAR(64) PRIMARY KEY,
    product_category_name VARCHAR(100),
    total_quantity_sold INT,
    total_revenue DECIMAL(14,2)
);

CREATE TABLE analytics_review_sentiment (
    product_category_name VARCHAR(100) PRIMARY KEY,
    avg_review_score DECIMAL(3,2),
    total_reviews INT
);

CREATE TABLE analytics_state_sales (
    customer_state VARCHAR(10) PRIMARY KEY,
    total_orders INT,
    total_revenue DECIMAL(14,2)
);
