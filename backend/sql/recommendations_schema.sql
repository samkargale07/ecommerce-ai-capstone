-- =========================================================
-- Recommendations Table — Day 5 ML Recommender
-- Stores pre-computed product-to-product recommendations
-- from two methods: collaborative (co-purchase) and content
-- (category + attribute similarity).
-- =========================================================

DROP TABLE IF EXISTS recommendations;

CREATE TABLE recommendations (
    product_id VARCHAR(64) NOT NULL,
    recommended_product_id VARCHAR(64) NOT NULL,
    method VARCHAR(20) NOT NULL,   -- 'collaborative' or 'content'
    score DECIMAL(10,4),
    PRIMARY KEY (product_id, recommended_product_id, method),
    INDEX idx_reco_product (product_id),
    INDEX idx_reco_method (method)
);
