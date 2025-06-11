🛠 T3 Chat Clone – Dev Action Plan (Split: Wyatt & Adam)
✅ Overview
We're building a multi-modal AI chat platform with model flexibility (text, image, video), auth-gated chat links, and advanced sharing capabilities. This doc outlines who does what to hit MVP.

🧠 Adam – Backend / Database Lead
🎯 Task 1: Chat & Media DB Design
 Create PostgreSQL (or SQLite) schemas for:

chat_sessions (one row per session)

messages (timestamped messages tied to sessions)

media_files (images/videos uploaded, linked to messages)

shared_access (tracks which users/emails can access which chats)

Example Tables:
sql
Copy
Edit
-- Chat sessions
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_public BOOLEAN DEFAULT FALSE
);

-- Messages
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES chat_sessions(id),
  role TEXT CHECK(role IN ('user', 'assistant')),
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Media
CREATE TABLE media_files (
  id UUID PRIMARY KEY,
  session_id UUID,
  filename TEXT,
  file_type TEXT CHECK(file_type IN ('image', 'video')),
  file_url TEXT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sharing Permissions
CREATE TABLE shared_access (
  session_id UUID,
  shared_with_email TEXT,
  can_edit BOOLEAN DEFAULT FALSE
);
🎯 Task 2: Auth + Shareable Chat Links
 Protect chat routes with auth (JWT or session-based)

 Generate unique share links per chat (UUID or slug)

 Add support for email-based access in shared_access

 Add /api/share route to POST emails to share with

🎯 Task 3: API Endpoints
 /api/chats/:id → fetch messages + media (auth check)

 /api/upload → handle image/video upload

 /api/models → return available models for frontend to load

🎨 Wyatt – Frontend + Model Loader
🎯 Task 1: Finalize Model Loading UI
 Load text, image, and video models from DB/API:

Claude, Gemini, GPT-4, DeepSeek, Ollama

Image models like SDXL, video ones like VideoCrafter

 Build UI filter/sort by model type

 Show provider name and capabilities (e.g. multi-modal, pricing)

🎯 Task 2: Frontend Auth + Share
 When opening chat by link:

 Check if the session is public

 Else ask user to log in

 Else check if their email is on the allowed list

 Show "Share this chat" UI with:

Public toggle

Invite by email

Copy link

🎯 Task 3: Final Chat Page Build
 Integrate DB-driven chat history + media display

 Support sending image/video prompts

 Add inline previews for media in chat

 Collaborate with Adam on request/response syncing

🔁 Joint Tasks
Task	Owner(s)
Setup DB connection	Adam
OAuth (Google?) auth	Wyatt
Finalize /chat/:id route	Both
Test session sharing	Both
Docs + GitHub README	Wyatt


 Working DB with chats, messages, media, sharing

 All model types load + run correctly

 Responsive chat UI with media support

 Shareable, secure URLs
