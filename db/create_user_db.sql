-- File: create_user_db.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user_accounts (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    subscription_plan TEXT NOT NULL DEFAULT 'free',
    token_quota INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    timezone TEXT
);