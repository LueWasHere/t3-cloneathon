**T3Chat Open Source Clone: Database Design Overview**

---

## 📁 Database Architecture Overview

This open-source chat platform mirrors T3 Chat’s core strengths: fast performance, model flexibility, clean UX, and efficient cost control. The database design reflects those goals by enabling:

* Scalable user management
* Chat session tracking per user
* Token and usage monitoring
* Flexibility across multiple AI models

The architecture assumes a relational database (PostgreSQL recommended) but can be adapted to other setups.

---

## 📆 Core Tables Explained

### 1. **Users Table (`users`)**

Stores all registered users and metadata.

| Column              | Type      | Purpose                               |
| ------------------- | --------- | ------------------------------------- |
| `id`                | UUID      | Primary key                           |
| `email`             | TEXT      | Login/account identity                |
| `hashed_password`   | TEXT      | Auth (or link to OAuth)               |
| `subscription_plan` | TEXT      | Tracks tier (e.g., free, premium)     |
| `token_quota`       | INTEGER   | Rate limit enforcement (e.g., 500/wk) |

Why: Central identity for users, with future-proof fields for subscriptions and quotas.

---

### 2. **Chats Table (`chats`)**

Represents each multi-turn conversation.

| Column          | Type      | Purpose                              |
| --------------- | --------- | ------------------------------------ |
| `id`            | UUID      | Primary key                          |
| `user_id`       | UUID      | Foreign key to `users`               |
| `title`         | TEXT      | Auto-generated title or user-defined |
| `created_at`    | TIMESTAMP | Used for filtering/sorting           |
| `model_used`    | TEXT      | Records which LLM was used           |
| `system_prompt` | TEXT      | Optional starter context             |

Why: Separates chats logically for display and retrieval, supports session resume.

---

### 3. **Messages Table (`messages`)**

Logs every user or AI message.

| Column                | Type      | Purpose                          |
| --------------------- | --------- | -------------------------------- |
| `id`                  | UUID      | Primary key                      |
| `chat_id`             | UUID      | Foreign key to `chats`           |
| `sender`              | TEXT      | 'user' or 'ai'                   |
| `message_content`     | TEXT      | Full message                     |
| `timestamp`           | TIMESTAMP | Message time                     |
| `model_response_time` | FLOAT     | Optional UX metric               |
| `tokens_used`         | INTEGER   | Required for quota/cost tracking |

Why: Enables token monitoring, real-time UI updates, and historical chat review.

---

### 4. **Usage Logs Table (`usage_logs`)**

Detailed logs for cost, throttling, and abuse prevention.

| Column        | Type      | Purpose                   |
| ------------- | --------- | ------------------------- |
| `id`          | UUID      | Primary key               |
| `user_id`     | UUID      | Foreign key to `users`    |
| `timestamp`   | TIMESTAMP | When the usage occurred   |
| `model`       | TEXT      | Which LLM was used        |
| `tokens_used` | INTEGER   | Actual API cost metric    |
| `status`      | TEXT      | success, throttled, error |

Why: Enables per-user and per-model analytics, cost tracking, throttling.

---

### 5. **Model Cache Table (Optional, `model_cache`)**

Useful for reusing prompt responses.

| Column              | Type      | Purpose                            |
| ------------------- | --------- | ---------------------------------- |
| `hash_prompt_input` | TEXT      | Deterministic hash of prompt input |
| `response`          | TEXT      | Saved model response               |
| `model`             | TEXT      | e.g., gpt-4, claude-3              |
| `created_at`        | TIMESTAMP | Expiry or invalidation reference   |

Why: Reduces cost and latency by caching frequent prompts.

---

## ⚖️ Design Philosophy

* **Modular**: Separated tables for flexibility and clarity
* **Token-aware**: Designed for rate limiting and cost analytics
* **LLM-agnostic**: Supports multiple models per chat or message
* **Scalable**: Index on user\_id, chat\_id, timestamps for performance

This schema is designed to support everything from a solo chat UI to a paid multi-user LLM access platform.

Let me know if you want the Prisma, SQL, or MongoDB implementation next.
