-- This script creates and populates the 'models' and 'image_models' tables.
-- It is designed to be run in a SQLite environment.

-- Use a transaction to ensure all commands succeed or none do.
BEGIN TRANSACTION;

-- =============================================================================
-- Drop existing tables to ensure a clean slate
-- =============================================================================
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS image_models;


-- =============================================================================
-- Create the table for Text and Multimodal Chat Models
-- =============================================================================
CREATE TABLE models (
    model_id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name                   TEXT    NOT NULL,
    model_name                      TEXT    NOT NULL,
    context_window                  INTEGER,
    supports_images_input           INTEGER, -- 0 for FALSE, 1 for TRUE
    supports_pdfs_input             INTEGER, -- 0 for FALSE, 1 for TRUE
    multimodal_input                INTEGER, -- 0 for FALSE, 1 for TRUE
    reasoning_enabled               INTEGER, -- 0 for FALSE, 1 for TRUE
    usd_per_million_input_tokens    REAL,
    usd_per_million_output_tokens   REAL,
    is_active                       INTEGER NOT NULL,
    notes                           TEXT
);


-- =============================================================================
-- Insert data into the 'models' table
-- =============================================================================
INSERT INTO models (provider_name, model_name, context_window, supports_images_input, supports_pdfs_input, multimodal_input, reasoning_enabled, usd_per_million_input_tokens, usd_per_million_output_tokens, is_active, notes) VALUES
('OpenAI', 'gpt-4o', 128000, 1, 1, 1, 1, 5.00, 15.00, 1, 'Flagship model. High performance across text, vision, and audio.'),
('OpenAI', 'gpt-4o-mini', 128000, 1, 1, 1, 1, 0.15, 0.60, 1, 'Fast, cost-effective model with gpt-4-turbo level intelligence.'),
('OpenAI', 'gpt-4-turbo', 128000, 1, 1, 1, 1, 10.00, 30.00, 1, 'Predecessor to gpt-4o. Still very capable.'),
('OpenAI', 'gpt-4', 8192, 0, 0, 0, 1, 30.00, 60.00, 1, 'Legacy model, largely superseded by Turbo and O-series.'),
('OpenAI', 'gpt-3.5-turbo', 16385, 0, 0, 0, 0, 0.50, 1.50, 1, 'Fast and affordable text-only model.'),
('OpenAI', 'gpt-4.1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 'Not a public API model name. Likely internal.'),
('OpenAI', 'chatgpt-4o-latest', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 'Not a public API model name. Refers to the model used in ChatGPT.'),
('OpenAI', 'o4-mini', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 'Alias for gpt-4o-mini. Use the official name.'),
('OpenAI', 'codex-mini-latest', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 'Codex models are deprecated and have been shut down.'),
('Anthropic', 'claude-3-opus-20240229', 200000, 1, 1, 1, 1, 15.00, 75.00, 1, 'Most powerful model for complex reasoning.'),
('Anthropic', 'claude-3.5-sonnet-20240620', 200000, 1, 1, 1, 1, 3.00, 15.00, 1, 'Flagship model. Faster and cheaper than Opus with similar intelligence.'),
('Anthropic', 'claude-3-sonnet-20240229', 200000, 1, 1, 1, 1, 3.00, 15.00, 1, 'Balanced model for performance and cost.'),
('Anthropic', 'claude-3-haiku-20240307', 200000, 1, 1, 1, 0, 0.25, 1.25, 1, 'Fastest and most compact model for near-instant responses.'),
('Google', 'gemini-1.5-pro', 1048576, 1, 1, 1, 1, 3.50, 10.50, 1, 'Large context. Price is for <128k context; higher for more.'),
('Google', 'gemini-1.5-flash', 1048576, 1, 1, 1, 1, 0.35, 1.05, 1, 'Large context. Price is for <128k context; higher for more.'),
('Google', 'gemini-2.5-pro-preview-06-05', NULL, 1, 1, 1, 1, NULL, NULL, 0, 'Private Preview. Details not public.'),
('xAI', 'grok-1', 32768, 0, 0, 0, 1, NULL, NULL, 1, 'Open-weights model. API access via Grok platform; pricing not public.'),
('xAI', 'grok-3-beta', 128000, 1, 1, 1, 1, NULL, NULL, 0, 'Private Preview on the Grok platform. Details not public.'),
('xAI', 'grok-3-mini-beta', 128000, 1, 1, 1, 1, NULL, NULL, 0, 'Private Preview on the Grok platform. Details not public.'),
('DeepSeek', 'deepseek-chat', 32768, 0, 0, 0, 1, 0.14, 0.28, 1, 'General purpose chat model.'),
('DeepSeek', 'deepseek-coder', 128000, 0, 0, 0, 1, 0.14, 0.28, 1, 'Specialized for code generation and understanding.'),
('Together.ai', 'meta-llama/Llama-3.1-405B-Instruct', 128000, 1, 1, 1, 1, 2.75, 2.75, 1, 'State-of-the-art open model for complex reasoning.'),
('Together.ai', 'meta-llama/Llama-3.1-70B-Instruct', 128000, 1, 1, 1, 1, 0.90, 0.90, 1, 'High-performance open model.'),
('Together.ai', 'meta-llama/Llama-3.1-8B-Instruct', 128000, 1, 1, 1, 0, 0.20, 0.20, 1, 'Efficient and capable small open model.'),
('Together.ai', 'google/gemma-2-27b-it', 16384, 0, 0, 0, 1, 0.30, 0.30, 1, 'Google''s powerful 27B open model.'),
('Together.ai', 'Qwen/Qwen2-72B-Instruct', 128000, 0, 0, 0, 1, 0.90, 0.90, 1, 'Top-tier multilingual model from Alibaba.'),
('Together.ai', 'databricks/dbrx-instruct', 32768, 0, 0, 0, 1, 1.00, 1.00, 1, 'Strong MoE model, especially for enterprise tasks.'),
('Together.ai', 'mistralai/Mixtral-8x22B-Instruct-v0.1', 65536, 0, 0, 0, 1, 1.20, 1.20, 1, 'Very large and powerful Sparse MoE model from Mistral.'),
('Together.ai', 'mistralai/Mixtral-8x7B-Instruct-v0.1', 32768, 0, 0, 0, 1, 0.60, 0.60, 1, 'Popular and efficient MoE model.'),
('Together.ai', 'mistralai/Mistral-7B-Instruct-v0.3', 32768, 0, 0, 0, 0, 0.20, 0.20, 1, 'Very popular and capable small model.');


-- =============================================================================
-- Create the table for Image Generation Models
-- =============================================================================
CREATE TABLE image_models (
    image_model_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name     TEXT    NOT NULL,
    model_name        TEXT    NOT NULL,
    max_resolution    TEXT,
    pricing_model     TEXT,
    is_active         INTEGER NOT NULL,
    notes             TEXT
);


-- =============================================================================
-- Insert data into the 'image_models' table
-- =============================================================================
INSERT INTO image_models (provider_name, model_name, max_resolution, pricing_model, is_active, notes) VALUES
('OpenAI', 'dall-e-3', '1792x1024', '$0.080 per image (HD)', 1, 'Highest quality image generation from OpenAI. Integrates well with GPT-4 for prompt enhancement.'),
('OpenAI', 'dall-e-2', '1024x1024', '$0.020 per image', 1, 'Older, faster, and cheaper model. Still available but superseded in quality by DALL-E 3.'),
('Google', 'imagen-3.0-generate-002', '4096x4096 (4K)', '$0.020 per image', 1, 'Google''s state-of-the-art model on Vertex AI. Known for photorealism and text rendering.'),
('Google', 'Veo (Video Model)', NULL, NULL, 0, 'In Private Preview. A video generation model, not a static image model. API is complex and not generally available.');


-- Finalize the transaction
COMMIT;