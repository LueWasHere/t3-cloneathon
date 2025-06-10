-- Create tables in data.db
-- Ran by app.py

PRAGMA foreign_keys = ON;

-- Table: chat_sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    chat_id TEXT PRIMARY KEY, -- UUID stored as TEXT
    user_id TEXT NOT NULL, -- Foreign key to user_accounts.user_id (in user.db)
    title TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    system_prompt TEXT,
    FOREIGN KEY (user_id) REFERENCES user_accounts(user_id)
);

-- Table: chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id TEXT PRIMARY KEY, -- UUID
    chat_id TEXT NOT NULL, -- Foreign key to chat_sessions.chat_id
    sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'ai')),
    message_text TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    model_used TEXT,
    FOREIGN KEY (chat_id) REFERENCES chat_sessions(chat_id)
);

-- Table: usage_metrics
CREATE TABLE IF NOT EXISTS usage_metrics (
    usage_id TEXT PRIMARY KEY, -- UUID
    user_id TEXT NOT NULL, -- Foreign key to user_accounts.user_id (in user.db)
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_name TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    status_code TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_accounts(user_id)
);

-- Table: model_capabilities
CREATE TABLE IF NOT EXISTS model_capabilities (
    model_id TEXT PRIMARY KEY, -- UUID
    provider_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    supports_images BOOLEAN NOT NULL DEFAULT 0,
    supports_pdfs BOOLEAN NOT NULL DEFAULT 0,
    multimodal_input BOOLEAN NOT NULL DEFAULT 0,
    reasoning_enabled BOOLEAN NOT NULL DEFAULT 0,
    max_token_limit INTEGER NOT NULL,
    usd_per_1k_tokens FLOAT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1
);
