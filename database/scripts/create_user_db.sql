-- Create the user_accounts table in user.db
-- Ran by app.py

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user_accounts (
    user_id TEXT PRIMARY KEY, -- UUID stored as TEXT
    email TEXT UNIQUE NOT NULL, -- Unique login
    hashed_password TEXT NOT NULL, -- Hashed password or OAuth ID
    subscription_plan TEXT NOT NULL CHECK (subscription_plan IN ('free', 'pro')),
    token_quota INTEGER NOT NULL DEFAULT 0, -- Remaining token quota
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Account creation timestamp
    timezone TEXT NOT NULL -- Timezone string, e.g., "America/Denver"
);
