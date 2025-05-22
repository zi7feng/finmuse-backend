CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    create_time TIMESTAMP DEFAULT NOW(),
    update_time TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    preferred_currency VARCHAR(10),
    risk_profile_level INTEGER,
    notification_opt_in BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'User'
);
