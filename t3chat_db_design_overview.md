# 📁 T3Chat Open Source Clone – Database Design

This repository documents the database schema for an open-source clone of T3 Chat: a blazing-fast, multi-model AI chat interface. This setup uses two databases to separate authentication data from chat interaction data.

---

## 🗃️ Database Overview

| Database     | Purpose                                      |
|--------------|-----------------------------------------------|
| `user.db`    | Manages authentication, account, and settings |
| `data.db`    | Handles chats, messages, usage, and models     |

---

## 🔐 `user.db`

### `user_accounts`
Stores user identity and subscription info.

| Column              | Type      | Notes                                  |
|---------------------|-----------|----------------------------------------|
| `user_id`           | UUID      | Primary key                            |
| `email`             | TEXT      | Unique login                           |
| `hashed_password`   | TEXT      | Hashed password or OAuth identifier    |
| `subscription_plan` | TEXT      | Plan tier (e.g., free, pro)            |
| `token_quota`       | INTEGER   | Remaining token quota                  |
| `created_at`        | TIMESTAMP | Account creation timestamp             |
| `timezone`          | TEXT      | Timezone string, e.g., "America/Denver" |

---

## 💬 `data.db`

### `chat_sessions`
Tracks individual conversations.

| Column          | Type      | Notes                              |
|-----------------|-----------|------------------------------------|
| `chat_id`       | UUID      | Primary key                        |
| `user_id`       | UUID      | FK to `user_accounts.user_id`      |
| `title`         | TEXT      | User-defined or AI-generated title |
| `created_at`    | TIMESTAMP | Timestamp of chat creation         |
| `system_prompt` | TEXT      | Optional system message seed       |

### `chat_messages`
Logs all messages exchanged in a session.

| Column            | Type      | Notes                                  |
|-------------------|-----------|----------------------------------------|
| `message_id`      | UUID      | Primary key                            |
| `chat_id`         | UUID      | FK to `chat_sessions.chat_id`          |
| `sender_type`     | TEXT      | Either 'user' or 'ai'                  |
| `message_text`    | TEXT      | Content of the message                 |
| `timestamp`       | TIMESTAMP | Message timestamp                      |
| `tokens_used`     | INTEGER   | Number of tokens used                  |
| `model_used`      | TEXT      | Model identifier (e.g., gpt-4o)        |

### `usage_metrics`
Tracks per-user API usage for billing and analytics.

| Column         | Type      | Notes                                      |
|----------------|-----------|--------------------------------------------|
| `usage_id`     | UUID      | Primary key                                |
| `user_id`      | UUID      | FK to `user_accounts.user_id`              |
| `timestamp`    | TIMESTAMP | Time of API interaction                    |
| `model_name`   | TEXT      | Model identifier used                      |
| `tokens_used`  | INTEGER   | Number of tokens used                      |
| `status_code`  | TEXT      | Outcome of request: success, error, etc.   |

### `model_capabilities`
Defines model features, capabilities, and pricing.

| Column               | Type    | Notes                                        |
|----------------------|---------|----------------------------------------------|
| `model_id`           | UUID    | Primary key                                  |
| `provider_name`      | TEXT    | e.g., OpenAI, Anthropic                      |
| `model_name`         | TEXT    | e.g., gpt-4o, claude-3-opus                  |
| `supports_images`    | BOOLEAN | Accepts image input                          |
| `supports_pdfs`      | BOOLEAN | Accepts PDF/document input                   |
| `multimodal_input`   | BOOLEAN | Supports combined vision + text input        |
| `reasoning_enabled`  | BOOLEAN | Optimized for complex reasoning and logic    |
| `max_token_limit`    | INTEGER | Maximum number of tokens per request         |
| `usd_per_1k_tokens`  | FLOAT   | Cost per 1,000 tokens in USD                 |
| `is_active`          | BOOLEAN | Indicates if model is currently available    |

---

## 🧠 Design Principles

- **Two DBs**: cleanly separates auth from AI interaction
- **Consistent Naming**: all column/table names are normalized and scoped
- **Token-Aware**: optimized for usage tracking and API cost modeling
- **Scalable**: pre-indexing on foreign keys and timestamps assumed

---

> **Repo by**: Wyatt Greene

