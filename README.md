# 🧬 T3 Chat Clone — Cloneathon 2025

Welcome to the **T3 Chat Clone** — a feature-rich, responsive, and open-source replica of the original **T3 Chat** platform, developed as part of the **first-ever Cloneathon**!

> Think Hackathon... but for *clones*.

This project recreates the core experience of T3 Chat: a sleek interface for chatting with a variety of AI models, switching between them, and managing your conversations — all in real time.

---

## 🚀 Features

- 💬 Multi-model chat interface (Ollama, OpenAI, etc.)
- ⚡ Switch between AI models on the fly
- 🧠 Message broadcasting to multiple models
- 🗃️ Conversation history with persistence
- 🌙 Dark mode support
- 💻 Built with modern tools (Flask, TailwindCSS, SQLite, etc.)

---

## 🛠️ Tech Stack

| Tool / Framework      | Purpose                       |
|-----------------------|-------------------------------|
| **Flask**             | Python backend                |
| **TailwindCSS**       | Utility-first styling         |
| **SQLite**            | Backend persistence           |

---

## 📸 Screenshots

> _Coming soon!_ Once we finish the UI, we'll drop in some before/after comparisons here.

---

## 🧰 Getting Started

1. **Clone the repo:**

```bash
git clone https://github.com/LueWasHere/t3-cloneathon.git
cd t3-cloneathon
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:

Create a .env file with your keys:

```ini
OPEN_AI=YOURAPIKEYHERE
CLAUDE=YOURAPIKEYHERE
GEMINI=YOURAPIKEYHERE
GROK=YOURAPIKEYHERE
TOGETHER_AI=YOURAPIKEYHERE
DEEPSEEK=YOURAPIKEYHERE
```

5. Run the Flask server:

```bash
flask run
```

## 🤝 Contributors
### Created with ☕, 🎧, and a touch of madness by:

#### _@LueWasHere_ – Adam Duncan
#### _@greene80501_ - Wyatt Green

> _Special thanks to the original T3 Chat team for the inspiration and oppurtunity._

## 📄 License
This project is for educational and non-commercial purposes only under the GNU General Public License.

## 🧠 About Cloneathon
Cloneathon is a new twist on the traditional hackathon. Instead of building from scratch, participants recreate existing sites to learn their inner workings, architecture, and design patterns.

Rebuild to understand. Clone to learn. 💡