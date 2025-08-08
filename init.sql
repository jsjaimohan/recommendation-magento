-- Database initialization script for recommendation system (MariaDB/MySQL)

-- Create database (if not exists)
-- CREATE DATABASE IF NOT EXISTS recommendations;

-- Use the database
USE recommendations;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    preferences JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP NULL,
    status VARCHAR(50) DEFAULT 'active'
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    attributes JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- Purchase transactions table (NEW for FBT)
CREATE TABLE IF NOT EXISTS purchase_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    order_id VARCHAR(255),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Transaction items table (NEW for FBT)
CREATE TABLE IF NOT EXISTS transaction_items (
    transaction_id VARCHAR(255),
    product_id VARCHAR(255),
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id, product_id),
    FOREIGN KEY (transaction_id) REFERENCES purchase_transactions(transaction_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- User behaviors table (ENHANCED for FBT)
CREATE TABLE IF NOT EXISTS user_behaviors (
    behavior_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    product_id VARCHAR(255),
    behavior_type VARCHAR(50) NOT NULL, -- view, cart, purchase, wishlist
    session_id VARCHAR(255),
    transaction_id VARCHAR(255) NULL, -- NEW: Link to purchase transaction
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES purchase_transactions(transaction_id) ON DELETE SET NULL
);

-- Product associations table (NEW for FBT)
CREATE TABLE IF NOT EXISTS product_associations (
    product_id VARCHAR(255),
    associated_product_id VARCHAR(255),
    support DECIMAL(5,4),      -- How often they appear together
    confidence DECIMAL(5,4),    -- How likely Y is bought with X
    lift DECIMAL(5,4),         -- How much more likely than random
    rule_type VARCHAR(50) DEFAULT 'frequently_bought_together',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, associated_product_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (associated_product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    product_id VARCHAR(255),
    score DECIMAL(5,4),
    algorithm_used VARCHAR(100),
    context JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- A/B Tests table
CREATE TABLE IF NOT EXISTS ab_tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    variants JSON NOT NULL,
    traffic_split JSON NOT NULL,
    start_date TIMESTAMP NULL,
    end_date TIMESTAMP NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_user_behaviors_user_id ON user_behaviors(user_id);
CREATE INDEX idx_user_behaviors_timestamp ON user_behaviors(timestamp);
CREATE INDEX idx_user_behaviors_type ON user_behaviors(behavior_type);
CREATE INDEX idx_user_behaviors_user_product ON user_behaviors(user_id, product_id);
CREATE INDEX idx_user_behaviors_complex ON user_behaviors(user_id, behavior_type, timestamp DESC);
CREATE INDEX idx_user_behaviors_transaction ON user_behaviors(transaction_id);

-- NEW: Indexes for FBT tables
CREATE INDEX idx_purchase_transactions_user_id ON purchase_transactions(user_id);
CREATE INDEX idx_purchase_transactions_date ON purchase_transactions(purchase_date);
CREATE INDEX idx_purchase_transactions_order_id ON purchase_transactions(order_id);

CREATE INDEX idx_transaction_items_product_id ON transaction_items(product_id);
CREATE INDEX idx_transaction_items_transaction_id ON transaction_items(transaction_id);

CREATE INDEX idx_product_associations_support ON product_associations(support DESC);
CREATE INDEX idx_product_associations_confidence ON product_associations(confidence DESC);
CREATE INDEX idx_product_associations_lift ON product_associations(lift DESC);
CREATE INDEX idx_product_associations_product_id ON product_associations(product_id);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_score ON recommendations(score DESC);
CREATE INDEX idx_recommendations_algorithm ON recommendations(algorithm_used);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_status ON products(status);

-- Insert sample data (optional)
-- INSERT INTO users (user_id, email, name) VALUES 
--     ('user_001', 'user1@example.com', 'John Doe'),
--     ('user_002', 'user2@example.com', 'Jane Smith');

-- INSERT INTO products (product_id, name, category, price) VALUES 
--     ('PROD001', 'iPhone 15 Pro', 'electronics', 999.99),
--     ('PROD002', 'Samsung Galaxy S24', 'electronics', 899.99);
