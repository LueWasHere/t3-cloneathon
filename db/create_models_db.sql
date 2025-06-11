-- ##################################################
-- ############## DATABASE SCHEMA SETUP #############
-- ##################################################

-- Drop tables if they exist to ensure a fresh start
DROP TABLE IF EXISTS llm_models;
DROP TABLE IF EXISTS image_models;
DROP TABLE IF EXISTS audio_models;
DROP TABLE IF EXISTS video_models;

-- Create the table for Language and Multimodal Models (LLMs)
CREATE TABLE llm_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    api_name VARCHAR(255),
    context_window_max_tokens INT,
    supports_images_input BOOLEAN DEFAULT FALSE,
    supports_pdfs_input BOOLEAN DEFAULT FALSE,
    multimodal_input BOOLEAN DEFAULT FALSE,
    reasoning_enabled BOOLEAN DEFAULT TRUE,
    usd_per_million_input_tokens DECIMAL(10, 5),
    usd_per_million_output_tokens DECIMAL(10, 5),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Create the table for Image Generation Models
CREATE TABLE image_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    api_name VARCHAR(255),
    context_window_max_tokens INT,
    supports_images_input BOOLEAN DEFAULT FALSE,
    supports_pdfs_input BOOLEAN DEFAULT FALSE,
    multimodal_input BOOLEAN DEFAULT FALSE,
    reasoning_enabled BOOLEAN DEFAULT FALSE,
    usd_per_million_input_tokens DECIMAL(10, 5),
    usd_per_million_output_tokens DECIMAL(10, 5),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Create the table for Audio Models (TTS, STT, etc.)
CREATE TABLE audio_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    api_name VARCHAR(255),
    context_window_max_tokens INT,
    supports_images_input BOOLEAN DEFAULT FALSE,
    supports_pdfs_input BOOLEAN DEFAULT FALSE,
    multimodal_input BOOLEAN DEFAULT TRUE,
    reasoning_enabled BOOLEAN DEFAULT FALSE,
    usd_per_million_input_tokens DECIMAL(10, 5),
    usd_per_million_output_tokens DECIMAL(10, 5),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Create the table for Video Generation Models
CREATE TABLE video_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(255) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    api_name VARCHAR(255),
    context_window_max_tokens INT,
    supports_images_input BOOLEAN DEFAULT TRUE,
    supports_pdfs_input BOOLEAN DEFAULT FALSE,
    multimodal_input BOOLEAN DEFAULT TRUE,
    reasoning_enabled BOOLEAN DEFAULT FALSE,
    usd_per_million_input_tokens DECIMAL(10, 5),
    usd_per_million_output_tokens DECIMAL(10, 5),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT
);


-- ##################################################
-- ############# POPULATE LLM_MODELS TABLE ############
-- ##################################################

INSERT INTO llm_models (provider_name, model_name, api_name, context_window_max_tokens, supports_images_input, supports_pdfs_input, multimodal_input, reasoning_enabled, usd_per_million_input_tokens, usd_per_million_output_tokens, is_active, notes) VALUES
-- Anthropic
('Anthropic', 'Claude Opus 4', 'claude-opus-4-20250514', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude Sonnet 4', 'claude-sonnet-4-20250514', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude Sonnet 3.7', 'claude-3-7-sonnet-20250219', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude Haiku 3.5', 'claude-3-5-haiku-20241022', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude Sonnet 3.5 v2', 'claude-3-5-sonnet-20241022-v2:0', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude Sonnet 3.5', 'claude-3-5-sonnet-20240620', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude 3 Opus', 'claude-3-opus-20240229', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude 3 Sonnet', 'claude-3-sonnet-20240229', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
('Anthropic', 'Claude 3 Haiku', 'claude-3-haiku-20240307', 200000, 1, 1, 1, 1, NULL, NULL, 1, 'Vision capable.'),
-- Google
('Google', 'Gemini 2.5 Flash Preview 05-20', 'gemini-2.5-flash-preview-05-20', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 2.5 Pro Preview', 'gemini-2.5-pro-preview-06-05', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 2.0 Flash', 'gemini-2.0-flash', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 2.0 Flash-Lite', 'gemini-2.0-flash-lite', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 1.5 Flash', 'gemini-1.5-flash', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 1.5 Flash-8B', 'gemini-1.5-flash-8b', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini 1.5 Pro', 'gemini-1.5-pro', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Input: Audio, images, videos, text.'),
('Google', 'Gemini Embedding', 'gemini-embedding-exp', NULL, 0, 0, 0, 0, NULL, NULL, 1, 'Type: Embedding.'),
-- OpenAI
('OpenAI', 'gpt-4.1', 'gpt-4.1-2025-04-14', 128000, 0, 1, 0, 1, 2.00, 8.00, 1, ''),
('OpenAI', 'gpt-4.1-mini', 'gpt-4.1-mini-2025-04-14', 128000, 0, 1, 0, 1, 0.40, 1.60, 1, ''),
('OpenAI', 'gpt-4.1-nano', 'gpt-4.1-nano-2025-04-14', 128000, 0, 1, 0, 1, 0.10, 0.40, 1, ''),
('OpenAI', 'gpt-4.5-preview', 'gpt-4.5-preview-2025-02-27', 128000, 1, 1, 1, 1, 75.00, 150.00, 1, 'Vision capable.'),
('OpenAI', 'gpt-4o', 'gpt-4o-2024-08-06', 128000, 1, 1, 1, 1, 2.50, 10.00, 1, 'Vision capable.'),
('OpenAI', 'gpt-4o-mini', 'gpt-4o-mini-2024-07-18', 128000, 1, 1, 1, 1, 0.15, 0.60, 1, 'Vision capable.'),
('OpenAI', 'o1', 'o1-2024-12-17', NULL, 1, 1, 1, 1, 15.00, 60.00, 1, 'Vision capable.'),
('OpenAI', 'o1-pro', 'o1-pro-2025-03-19', NULL, 1, 1, 1, 1, 150.00, 600.00, 1, 'Vision capable.'),
('OpenAI', 'o3', 'o3-2025-04-16', NULL, 1, 1, 1, 1, 10.00, 40.00, 1, 'Vision capable.'),
('OpenAI', 'o4-mini', 'o4-mini-2025-04-16', NULL, 1, 1, 1, 1, 1.10, 4.40, 1, 'Vision capable.'),
('OpenAI', 'o3-mini', 'o3-mini-2025-01-31', NULL, 1, 1, 1, 1, 1.10, 4.40, 1, 'Vision capable.'),
('OpenAI', 'o1-mini', 'o1-mini-2024-09-12', NULL, 1, 1, 1, 1, 1.10, 4.40, 1, 'Vision capable.'),
('OpenAI', 'codex-mini-latest', 'codex-mini-latest', NULL, 0, 0, 0, 1, 1.50, 6.00, 1, 'Type: Code-specific.'),
('OpenAI', 'gpt-4o-mini-search-preview', 'gpt-4o-mini-search-preview-2025-03-11', 128000, 1, 1, 1, 1, 0.15, 0.60, 1, 'Optimized for search.'),
('OpenAI', 'gpt-4o-search-preview', 'gpt-4o-search-preview-2025-03-11', 128000, 1, 1, 1, 1, 2.50, 10.00, 1, 'Optimized for search.'),
('OpenAI', 'computer-use-preview', 'computer-use-preview-2025-03-11', NULL, 1, 1, 1, 1, 3.00, 12.00, 1, 'Specialized for computer interaction.'),
-- DeepSeek
('DeepSeek', 'deepseek-chat', 'deepseek-chat', 64000, 0, 1, 0, 1, 0.27, 1.10, 1, 'Type: Chat. Discounted prices available.'),
('DeepSeek', 'deepseek-reasoner', 'deepseek-reasoner', 64000, 0, 1, 0, 1, 0.55, 2.19, 1, 'Type: Chat. Discounted prices available.'),
-- TogetherAI and other providers
('WhereIsAI', 'UAE-Large-V1', 'WhereIsAI/UAE-Large-V1', NULL, 0, 0, 0, 0, 0.016, 0.016, 1, 'Type: embedding.'),
('Meta', 'Llama-3.2-3B-Instruct-Turbo', 'meta-llama/Llama-3.2-3B-Instruct-Turbo', 131072, 0, 1, 0, 1, 0.06, 0.06, 1, 'Type: chat.'),
('Arcee AI', 'coder-large', 'arcee-ai/coder-large', 32768, 0, 1, 0, 1, 0.5, 0.8, 1, 'Type: chat. Specialized for coding.'),
('Meta', 'Llama-Guard-4-12B', 'meta-llama/Llama-Guard-4-12B', 1048576, 1, 1, 1, 0, 0.2, 0.2, 1, 'Type: moderation. Vision capable.'),
('Together', 'm2-bert-80M-32k-retrieval', 'togethercomputer/m2-bert-80M-32k-retrieval', 32768, 0, 1, 0, 0, 0.008, 0.008, 1, 'Type: embedding.'),
('BAAI', 'bge-large-en-v1.5', 'BAAI/bge-large-en-v1.5', 512, 0, 0, 0, 0, 0.016, 0.016, 1, 'Type: embedding.'),
('Arcee AI', 'arcee-blitz', 'arcee-ai/arcee-blitz', 32768, 0, 1, 0, 1, 0.45, 0.75, 1, 'Type: chat.'),
('LG AI', 'exaone-3-5-32b-instruct', 'lgai/exaone-3-5-32b-instruct', 32768, 0, 1, 0, 1, 0.0, 0.0, 1, 'Type: chat.'),
('Meta', 'LLaMA-2 (70B)', 'meta-llama-llama-2-70b-hf', 4096, 0, 1, 0, 1, 0.9, 0.9, 1, 'Type: language.'),
('Refuel AI', 'Refuel-Llm-V2', 'togethercomputer/Refuel-Llm-V2', 16384, 0, 1, 0, 1, 0.6, 0.6, 1, 'Type: chat.'),
('Intfloat', 'multilingual-e5-large-instruct', 'intfloat/multilingual-e5-large-instruct', 514, 0, 0, 0, 0, 0.02, 0.02, 1, 'Type: embedding.'),
('Gryphe', 'MythoMax-L2 (13B)', 'Gryphe/MythoMax-L2-13b', 4096, 0, 1, 0, 1, 0.3, 0.3, 1, 'Type: chat.'),
('Alibaba Nlp', 'Gte Modernbert Base', 'Alibaba-NLP/gte-modernbert-base', 8192, 0, 1, 0, 0, 0.08, 0.08, 1, 'Type: embedding.'),
('Meta', 'Llama-3.3-70B-Instruct-Turbo', 'meta-llama/Llama-3.3-70B-Instruct-Turbo', 131072, 0, 1, 0, 1, 0.88, 0.88, 1, 'Type: chat.'),
('Meta', 'LlamaGuard-2-8b', 'meta-llama/LlamaGuard-2-8b', 8192, 0, 1, 0, 0, 0.2, 0.2, 1, 'Type: moderation.'),
('Together', 'm2-bert-80M-8k-retrieval', 'togethercomputer/m2-bert-80M-8k-retrieval', 8192, 0, 1, 0, 0, 0.008, 0.008, 1, 'Type: embedding.'),
('DeepSeek', 'DeepSeek-R1', 'deepseek-ai/DeepSeek-R1', 163840, 0, 1, 0, 1, 3.0, 7.0, 1, 'Type: chat.'),
('Qwen', 'Qwen3-235B-A22B-fp8-tput', 'Qwen/Qwen3-235B-A22B-fp8-tput', 40960, 0, 1, 0, 1, 0.2, 0.6, 1, 'Type: chat.'),
('Nousresearch', 'Nous-Hermes-2-Mixtral-8x7B-DPO', 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO', 32768, 0, 1, 0, 1, 0.6, 0.6, 1, 'Type: chat.'),
('Meta', 'Llama-3-70B-Instruct-Turbo', 'meta-llama/Meta-Llama-3-70B-Instruct-Turbo', 8192, 0, 1, 0, 1, 0.88, 0.88, 1, 'Type: chat.'),
('Gryphe', 'Gryphe MythoMax L2 Lite (13B)', 'Gryphe/MythoMax-L2-13b-Lite', 4096, 0, 1, 0, 1, 0.1, 0.1, 1, 'Type: chat.'),
('Meta', 'Llama-Guard-3-8B', 'meta-llama/Meta-Llama-Guard-3-8B', 8192, 0, 1, 0, 0, 0.2, 0.2, 1, 'Type: moderation.'),
('DeepSeek', 'DeepSeek-V3', 'deepseek-ai/DeepSeek-V3', 131072, 0, 1, 0, 1, 1.25, 1.25, 1, 'Type: chat.'),
('mistralai', 'Mixtral-8x7B-Instruct-v0.1', 'mistralai/Mixtral-8x7B-Instruct-v0.1', 32768, 0, 1, 0, 1, 0.6, 0.6, 1, 'Type: chat.'),
('nvidia', 'Llama-3.1-Nemotron-70B-Instruct-HF', 'nvidia/Llama-3.1-Nemotron-70B-Instruct-HF', 32768, 0, 1, 0, 1, 0.88, 0.88, 1, 'Type: chat.'),
('Meta', 'Llama-3.2-90B-Vision-Instruct-Turbo', 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo', 131072, 1, 1, 1, 1, 1.2, 1.2, 1, 'Vision capable.'),
('Arcee AI', 'virtuoso-large', 'arcee-ai/virtuoso-large', 131072, 0, 1, 0, 1, 0.75, 1.2, 1, 'Type: chat. Specialized for reasoning.'),
('Arcee AI', 'virtuoso-medium-v2', 'arcee-ai/virtuoso-medium-v2', 131072, 0, 1, 0, 1, 0.5, 0.8, 1, 'Type: chat.'),
('Qwen', 'Qwen2.5-VL-72B-Instruct', 'Qwen/Qwen2.5-VL-72B-Instruct', 32768, 1, 1, 1, 1, 1.95, 8.0, 1, 'Vision capable.'),
('Meta', 'Llama-4-Scout-17B-16E-Instruct', 'meta-llama/Llama-4-Scout-17B-16E-Instruct', 1048576, 1, 1, 1, 1, 0.18, 0.59, 1, 'Vision capable.'),
('DeepSeek', 'DeepSeek-R1-Distill-Llama-70B', 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B', 131072, 0, 1, 0, 1, 2.0, 2.0, 1, 'Type: chat.'),
('Meta', 'Llama-3.2-11B-Vision-Instruct-Turbo', 'meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo', 131072, 1, 1, 1, 1, 0.18, 0.18, 1, 'Vision capable.'),
('Google', 'gemma-2-27b-it', 'google/gemma-2-27b-it', 8192, 0, 1, 0, 1, 0.8, 0.8, 1, 'Type: chat.'),
('mistralai', 'Mistral-Small-24B-Instruct-2501', 'mistralai/Mistral-Small-24B-Instruct-2501', 32768, 0, 1, 0, 1, 0.8, 0.8, 1, 'Type: chat.'),
('DeepSeek', 'DeepSeek-R1-Distill-Llama-70B-free', 'deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free', 8192, 0, 1, 0, 1, 0.0, 0.0, 1, 'Type: chat.'),
('Qwen', 'Qwen2.5-Coder-32B-Instruct', 'Qwen/Qwen2.5-Coder-32B-Instruct', 16384, 0, 1, 0, 1, 0.8, 0.8, 1, 'Type: chat. Specialized for code.'),
('Meta', 'Llama-3-70b-chat-hf', 'meta-llama/Llama-3-70b-chat-hf', 8192, 0, 1, 0, 1, 0.88, 0.88, 1, 'Type: chat.'),
('Meta', 'Llama-Vision-Free', 'meta-llama/Llama-Vision-Free', 131072, 1, 1, 1, 1, 0.0, 0.0, 1, 'Vision capable.'),
('Meta', 'Llama-3-8b-chat-hf', 'meta-llama/Llama-3-8b-chat-hf', 8192, 0, 1, 0, 1, 0.2, 0.2, 1, 'Type: chat.'),
('mistralai', 'Mistral-7B-Instruct-v0.1', 'mistralai/Mistral-7B-Instruct-v0.1', 32768, 0, 1, 0, 1, 0.2, 0.2, 1, 'Type: chat.'),
('Qwen', 'Qwen2.5-7B-Instruct-Turbo', 'Qwen/Qwen2.5-7B-Instruct-Turbo', 32768, 0, 1, 0, 1, 0.3, 0.3, 1, 'Type: chat.'),
('Meta', 'Llama-3.1-70B-Instruct-Turbo', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo', 131072, 0, 1, 0, 1, 0.88, 0.88, 1, 'Type: chat.'),
('Meta', 'Llama-3.1-405B-Instruct-Turbo', 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 130815, 1, 1, 1, 1, 3.5, 3.5, 1, 'Vision capable.'),
('Meta', 'Llama-3-8B-Instruct-Lite', 'meta-llama/Meta-Llama-3-8B-Instruct-Lite', 8192, 0, 1, 0, 1, 0.1, 0.1, 1, 'Type: chat.'),
('Meta', 'Llama-4-Maverick-17B-128E-Instruct-FP8', 'meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8', 1048576, 1, 1, 1, 1, 0.27, 0.85, 1, 'Vision capable.'),
('mistralai', 'Mistral-7B-Instruct-v0.2', 'mistralai/Mistral-7B-Instruct-v0.2', 32768, 0, 1, 0, 1, 0.2, 0.2, 1, 'Type: chat.'),
('Meta', 'Llama-3.1-8B-Instruct-Turbo', 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo', 131072, 0, 1, 0, 1, 0.18, 0.18, 1, 'Type: chat.'),
('Qwen', 'Qwen2-72B-Instruct', 'Qwen/Qwen2-72B-Instruct', 32768, 0, 1, 0, 1, 0.9, 0.9, 1, 'Type: chat.'),
('mistralai', 'Mistral-7B-Instruct-v0.3', 'mistralai/Mistral-7B-Instruct-v0.3', 32768, 0, 1, 0, 1, 0.2, 0.2, 1, 'Type: chat.'),
('salesforce', 'Llama-Rank-V1', 'Salesforce/Llama-Rank-V1', 8192, 0, 1, 0, 0, 0.1, 0.1, 1, 'Type: rerank.'),
('Meta', 'Llama-Guard-3-11B-Vision-Turbo', 'meta-llama/Llama-Guard-3-11B-Vision-Turbo', 131072, 1, 1, 1, 0, 0.18, 0.18, 1, 'Type: moderation. Vision capable.'),
('BAAI', 'bge-base-en-v1.5', 'BAAI/bge-base-en-v1.5', 512, 0, 0, 0, 0, 0.008, 0.008, 1, 'Type: embedding.'),
('Qwen', 'Qwen2-VL-72B-Instruct', 'Qwen/Qwen2-VL-72B-Instruct', 32768, 1, 1, 1, 1, 1.2, 1.2, 1, 'Vision capable.'),
('Mixedbread AI', 'Mxbai-Rerank-Large-V2', 'mixedbread-ai/Mxbai-Rerank-Large-V2', 32768, 0, 1, 0, 0, 0.1, 0.1, 1, 'Type: rerank.');


-- #####################################################
-- ############# POPULATE IMAGE_MODELS TABLE ############
-- #####################################################

INSERT INTO image_models (provider_name, model_name, api_name, context_window_max_tokens, supports_images_input, supports_pdfs_input, multimodal_input, reasoning_enabled, usd_per_million_input_tokens, usd_per_million_output_tokens, is_active, notes) VALUES
('Google', 'Gemini 2.0 Flash Preview Image Generation', 'gemini-2.0-flash-preview-image-generation', 1000000, 1, 1, 1, 0, NULL, NULL, 1, 'Conversational image generation and editing.'),
('Google', 'Imagen 3', 'imagen-3.0-generate-002', NULL, 0, 0, 0, 0, NULL, NULL, 1, 'Text-to-Image.'),
('OpenAI', 'gpt-image-1', 'gpt-image-1', NULL, 0, 0, 0, 0, 5.00, NULL, 1, 'Text-to-Image. Price is per 1M input tokens.'),
('Black Forest Labs', 'FLUX.1 [schnell] Free', 'black-forest-labs/FLUX.1-schnell-Free', NULL, 0, 0, 0, 0, 0.0, 0.0, 1, 'Free Text-to-Image model.'),
('Black Forest Labs', 'FLUX1.1 [pro]', 'black-forest-labs/FLUX.1.1-pro', NULL, 0, 0, 0, 0, NULL, NULL, 1, 'Pro Text-to-Image model.'),
('Black Forest Labs', 'FLUX.1 Redux [dev]', 'black-forest-labs/FLUX.1-redux', NULL, 0, 0, 0, 0, 0.0, 0.0, 1, 'Text-to-Image.'),
('Black Forest Labs', 'FLUX.1 Depth [dev]', 'black-forest-labs/FLUX.1-depth', NULL, 1, 0, 1, 0, 0.0, 0.0, 1, 'ControlNet-style depth model.'),
('Black Forest Labs', 'FLUX.1 Canny [dev]', 'black-forest-labs/FLUX.1-canny', NULL, 1, 0, 1, 0, 0.0, 0.0, 1, 'ControlNet-style canny model.'),
('Black Forest Labs', 'FLUX.1 [dev] LoRA', 'black-forest-labs/FLUX.1-dev-lora', NULL, 0, 0, 0, 0, 0.0, 0.0, 1, 'Supports LoRA.'),
('Black Forest Labs', 'FLUX.1 [dev]', 'black-forest-labs/FLUX.1-dev', NULL, 0, 0, 0, 0, 0.0, 0.0, 1, 'Text-to-Image.'),
('Black Forest Labs', 'FLUX.1 Schnell', 'black-forest-labs/FLUX.1-schnell', NULL, 0, 0, 0, 0, 0.0, 0.0, 1, 'Text-to-Image.');


-- ####################################################
-- ############# POPULATE AUDIO_MODELS TABLE ############
-- ####################################################

INSERT INTO audio_models (provider_name, model_name, api_name, context_window_max_tokens, supports_images_input, supports_pdfs_input, multimodal_input, reasoning_enabled, usd_per_million_input_tokens, usd_per_million_output_tokens, is_active, notes) VALUES
('Google', 'Gemini 2.5 Flash Native Audio', 'gemini-2.5-flash-preview-native-audio-dialog', NULL, 0, 0, 1, 1, NULL, NULL, 1, 'Conversational Audio. Input: Audio, videos, text. Output: Text and audio.'),
('Google', 'Gemini 2.5 Flash Preview TTS', 'gemini-2.5-flash-preview-tts', NULL, 0, 0, 1, 0, NULL, NULL, 1, 'Text-to-Speech. Output: Audio.'),
('Google', 'Gemini 2.5 Pro Preview TTS', 'gemini-2.5-pro-preview-tts', NULL, 0, 0, 1, 0, NULL, NULL, 1, 'Text-to-Speech. Output: Audio.'),
('Google', 'Gemini 2.0 Flash Live', 'gemini-2.0-flash-live-001', 1000000, 1, 1, 1, 1, NULL, NULL, 1, 'Conversational Audio/Video. Low-latency bidirectional voice and video.'),
('OpenAI', 'gpt-4o-audio-preview', 'gpt-4o-audio-preview-2024-12-17', 128000, 1, 1, 1, 1, 40.00, 80.00, 1, 'Pricing is specific to audio tokens.'),
('OpenAI', 'gpt-4o-realtime-preview', 'gpt-4o-realtime-preview-2024-12-17', 128000, 1, 1, 1, 1, 40.00, 80.00, 1, 'Pricing is specific to audio tokens.'),
('OpenAI', 'gpt-4o-mini-audio-preview', 'gpt-4o-mini-audio-preview-2024-12-17', 128000, 1, 1, 1, 1, 10.00, 20.00, 1, 'Pricing is specific to audio tokens.'),
('OpenAI', 'gpt-4o-mini-realtime-preview', 'gpt-4o-mini-realtime-preview-2024-12-17', 128000, 1, 1, 1, 1, 10.00, 20.00, 1, 'Pricing is specific to audio tokens.'),
('Cartesia', 'sonic', 'cartesia/sonic', NULL, 0, 0, 1, 0, 65.0, 0.0, 1, 'Text-to-Speech. Input price is per 1M characters, not tokens.'),
('Cartesia', 'sonic-2', 'cartesia/sonic-2', NULL, 0, 0, 1, 0, 65.0, 0.0, 1, 'Text-to-Speech. Input price is per 1M characters, not tokens.');

-- ####################################################
-- ############# POPULATE VIDEO_MODELS TABLE ############
-- ####################################################

INSERT INTO video_models (provider_name, model_name, api_name, context_window_max_tokens, supports_images_input, supports_pdfs_input, multimodal_input, reasoning_enabled, usd_per_million_input_tokens, usd_per_million_output_tokens, is_active, notes) VALUES
('Google', 'Veo 2', 'veo-2.0-generate-001', NULL, 1, 0, 1, 0, NULL, NULL, 1, 'Video Generation. Input: Text, images. Output: Video.');