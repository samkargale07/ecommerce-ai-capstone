-- =========================================================
-- E-commerce AI Capstone — MySQL Schema
-- Run this AFTER creating the database:
--   CREATE DATABASE ecommerce_capstone;
--   USE ecommerce_capstone;
-- =========================================================

-- Drop tables if re-running (child tables first, to respect FK constraints)
DROP TABLE IF EXISTS order_reviews;
DROP TABLE IF EXISTS order_payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS category_translation;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS customers;

-- =========================================================
-- CUSTOMERS
-- =========================================================
CREATE TABLE customers (
    customer_id VARCHAR(64) PRIMARY KEY,
    customer_unique_id VARCHAR(64) NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(10),
    INDEX idx_customer_unique (customer_unique_id),
    INDEX idx_customer_state (customer_state)
);

-- =========================================================
-- SELLERS
-- =========================================================
CREATE TABLE sellers (
    seller_id VARCHAR(64) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(10),
    seller_city VARCHAR(100),
    seller_state VARCHAR(10),
    INDEX idx_seller_state (seller_state)
);

-- =========================================================
-- CATEGORY TRANSLATION (Portuguese -> English)
-- =========================================================
CREATE TABLE category_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);

-- =========================================================
-- PRODUCTS
-- =========================================================
CREATE TABLE products (
    product_id VARCHAR(64) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT,
    FOREIGN KEY (product_category_name) REFERENCES category_translation(product_category_name)
        ON DELETE SET NULL,
    INDEX idx_product_category (product_category_name)
);

-- =========================================================
-- ORDERS
-- =========================================================
CREATE TABLE orders (
    order_id VARCHAR(64) PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    order_status VARCHAR(30),
    order_purchase_timestamp DATETIME,
    order_approved_at DATETIME,
    order_delivered_carrier_date DATETIME,
    order_delivered_customer_date DATETIME,
    order_estimated_delivery_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE,
    INDEX idx_order_status (order_status),
    INDEX idx_order_purchase_date (order_purchase_timestamp)
);

-- =========================================================
-- ORDER ITEMS (line items — one order can have many)
-- =========================================================
CREATE TABLE order_items (
    order_id VARCHAR(64) NOT NULL,
    order_item_id INT NOT NULL,
    product_id VARCHAR(64) NOT NULL,
    seller_id VARCHAR(64) NOT NULL,
    shipping_limit_date DATETIME,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE,
    INDEX idx_item_product (product_id),
    INDEX idx_item_seller (seller_id)
);

-- =========================================================
-- ORDER PAYMENTS (one order can have multiple payment entries)
-- =========================================================
CREATE TABLE order_payments (
    order_id VARCHAR(64) NOT NULL,
    payment_sequential INT NOT NULL,
    payment_type VARCHAR(30),
    payment_installments INT,
    payment_value DECIMAL(10,2),
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    INDEX idx_payment_type (payment_type)
);

-- =========================================================
-- ORDER REVIEWS
-- =========================================================
CREATE TABLE order_reviews (
    review_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    review_score INT,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date DATETIME,
    review_answer_timestamp DATETIME,
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    INDEX idx_review_score (review_score)
);
