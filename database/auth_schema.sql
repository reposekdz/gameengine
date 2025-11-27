-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role ENUM('user', 'admin', 'pro') DEFAULT 'user',
    subscription_tier ENUM('free', 'monthly', 'annual', 'pro') DEFAULT 'free',
    subscription_status ENUM('active', 'cancelled', 'expired') DEFAULT 'active',
    subscription_start DATETIME,
    subscription_end DATETIME,
    stripe_customer_id VARCHAR(255),
    paypal_customer_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_subscription (subscription_tier, subscription_status)
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    plan_type ENUM('monthly', 'annual', 'pro') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status ENUM('active', 'cancelled', 'expired', 'pending') DEFAULT 'pending',
    payment_method ENUM('stripe', 'paypal', 'crypto') NOT NULL,
    payment_id VARCHAR(255),
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_subscription (user_id, status)
);

-- Usage Limits Table
CREATE TABLE IF NOT EXISTS usage_limits (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    subscription_tier ENUM('free', 'monthly', 'annual', 'pro') NOT NULL,
    generations_limit INT DEFAULT 0,
    generations_used INT DEFAULT 0,
    downloads_limit INT DEFAULT 0,
    downloads_used INT DEFAULT 0,
    storage_limit_gb INT DEFAULT 0,
    storage_used_gb DECIMAL(10, 2) DEFAULT 0,
    api_calls_limit INT DEFAULT 0,
    api_calls_used INT DEFAULT 0,
    reset_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_limits (user_id)
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    subscription_id VARCHAR(36),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method ENUM('stripe', 'paypal', 'crypto') NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    transaction_id VARCHAR(255),
    payment_intent_id VARCHAR(255),
    description TEXT,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL,
    INDEX idx_user_payments (user_id),
    INDEX idx_payment_status (payment_status)
);

-- Downloads Table
CREATE TABLE IF NOT EXISTS downloads (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    asset_id VARCHAR(36) NOT NULL,
    asset_type ENUM('model', 'texture', 'game', 'animation', 'audio') NOT NULL,
    file_format VARCHAR(10) NOT NULL,
    file_size_mb DECIMAL(10, 2) NOT NULL,
    download_url TEXT,
    expires_at DATETIME,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_downloads (user_id),
    INDEX idx_asset_downloads (asset_id)
);

-- Pay-Per-Use Table
CREATE TABLE IF NOT EXISTS pay_per_use (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    item_type ENUM('generation', 'download', 'game', 'model', 'texture') NOT NULL,
    item_id VARCHAR(36),
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    payment_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_payperuse (user_id)
);

-- API Keys Table
CREATE TABLE IF NOT EXISTS api_keys (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_used DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_api_key (api_key),
    INDEX idx_user_keys (user_id)
);

-- Subscription Plans Table
CREATE TABLE IF NOT EXISTS subscription_plans (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    tier ENUM('free', 'monthly', 'annual', 'pro') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    billing_period ENUM('monthly', 'annual', 'lifetime') NOT NULL,
    generations_limit INT DEFAULT 0,
    downloads_limit INT DEFAULT 0,
    storage_limit_gb INT DEFAULT 0,
    api_calls_limit INT DEFAULT 0,
    features JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert Default Plans
INSERT INTO subscription_plans (id, name, tier, price, billing_period, generations_limit, downloads_limit, storage_limit_gb, api_calls_limit, features) VALUES
('plan-free', 'Free', 'free', 0.00, 'monthly', 10, 0, 1, 100, '{"download": false, "quality": "standard"}'),
('plan-monthly', 'Monthly Pro', 'monthly', 29.99, 'monthly', 1000, 1000, 100, 10000, '{"download": true, "quality": "ultra", "priority": true}'),
('plan-annual', 'Annual Pro', 'annual', 299.99, 'annual', 20000, 20000, 1000, 200000, '{"download": true, "quality": "ultra", "priority": true, "discount": "20%"}'),
('plan-pro', 'Pro Unlimited', 'pro', 0.00, 'lifetime', -1, -1, -1, -1, '{"download": true, "quality": "ultra", "priority": true, "unlimited": true, "admin": true}');

-- Insert Admin User
INSERT INTO users (id, email, password_hash, full_name, role, subscription_tier, subscription_status) VALUES
('admin-001', 'reponsekdz06@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfQC8mq8S6', 'Admin User', 'admin', 'pro', 'active');
