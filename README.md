# PolyMind AI 🧠⚡

> **Multi-Model Intelligent Chat Platform with Document Intelligence, Vision AI, Voice Input & RAG**

PolyMind AI is a full-stack AI-powered chat platform built with Django REST Framework and LangChain. It supports multi-provider LLM routing (Mistral AI, OpenAI, Gemini, Groq), intelligent PDF document Q&A via RAG, real-time camera image capture with Vision AI analysis, voice-to-text input, and conversation history management.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Model AI Chat** | Seamless switching between Mistral (Tiny/Small/Medium/Large/Codestral), GPT-4o, Gemini 2.0, Llama 3.3 70B, Groq |
| 📄 **PDF Document Intelligence** | Upload PDFs and perform RAG-based Q&A with page-level source citations |
| 📸 **Camera Image Capture** | Live camera feed with capture, retake, and Vision AI analysis |
| 🖼️ **Image File Attachment** | Attach images directly to queries for multimodal AI responses |
| 🗣️ **Voice Input (Speech-to-Text)** | Real-time voice transcription using the browser's Web Speech API |
| ⚡ **Quick Prompt Templates** | 10 professional prompt templates (Summarize, Key Points, ELI5, Quiz, etc.) |
| 💾 **Export Conversations** | Download full chat history as Markdown |
| 📜 **Chat History** | Persistent session management with per-session document context |
| 🔑 **Per-User API Keys** | Each user stores their own provider API keys securely in their profile |
| 🔐 **JWT Authentication** | Secure login, registration, token refresh, and blacklist-on-logout |
| 👤 **User Profile** | Edit personal info, change password, view document stats |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Django 5 + Django REST Framework |
| **AI Framework** | LangChain + LangChain-OpenAI |
| **Vector DB** | ChromaDB (local persistent) |
| **Multi-Model LLMs** | Mistral AI, OpenAI, OpenRouter, Google Gemini, Groq |
| **Auth** | JWT (djangorestframework-simplejwt) |
| **Frontend** | Vanilla JS + Tailwind CSS (CDN) + Lucide Icons |
| **Voice** | Web Speech API (Browser native) |
| **Vision** | Multimodal message payloads via OpenAI-compatible API |
| **Database** | SQLite (dev) / PostgreSQL (prod) |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/polymind-ai.git
cd polymind-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True

# Optional server-level defaults (users can also set their own keys via UI)
OPENROUTER_API_KEY=sk-or-v1-...
MISTRAL_API_KEY=...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

> **Note:** API keys can also be set per-user via the **API Keys** settings page in the UI. Free tier works with OpenRouter (Mistral 7B, Llama 3.3 70B, Gemini 2.0 Flash).

### 5. Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser  # optional admin access
```

### 6. Start Development Server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** → Register → Start chatting!

---

## 🌐 Pages

| URL | Description |
|-----|-------------|
| `/` or `/chat/` | Main Chat Interface |
| `/auth/` | Login & Register |
| `/settings/` | API Keys & Default Model Configuration |
| `/profile/` | User Profile, Password Change |
| `/admin/` | Django Admin Panel |

---

## 📡 REST API Endpoints

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/users/register/` | Create account |
| `POST` | `/api/users/login/` | Login (get JWT tokens) |
| `POST` | `/api/users/logout/` | Logout (blacklist refresh token) |
| `GET/PATCH` | `/api/users/profile/` | View & update profile + API keys |
| `POST` | `/api/users/change-password/` | Change password |

### Documents & AI
| Method | URL | Description |
|--------|-----|-------------|
| `POST` | `/api/documents/upload/` | Upload & index PDF |
| `GET` | `/api/documents/` | List all documents |
| `GET/PATCH/DELETE` | `/api/documents/<id>/` | Document detail |
| `POST` | `/api/documents/ask/` | General AI chat (text + image) |
| `POST` | `/api/documents/<id>/ask/` | Document-grounded Q&A with RAG |
| `GET` | `/api/documents/<id>/summary/` | Auto-generated summary |
| `GET` | `/api/documents/models/` | List all supported AI models |
| `GET` | `/api/documents/chats/` | List general chat sessions |
| `GET/DELETE` | `/api/documents/chats/<id>/` | Session detail / delete |
| `GET` | `/api/documents/dashboard/` | Dashboard stats |

---

## 🤖 Supported AI Models

### OpenRouter (Free Tier Models)
- `openrouter/free` — Dynamic Auto-Router to active free models
- `mistralai/mistral-small-24b-instruct-2501:free` — Mistral Small 3 24B
- `mistralai/mistral-nemo:free` — Mistral Nemo 12B (128k context)
- `google/gemini-2.0-flash-exp:free` — Next-gen Google multimodal
- `meta-llama/llama-3.3-70b-instruct:free` — Llama 3.3 70B
- `deepseek/deepseek-r1:free` — DeepSeek R1 reasoning
- `qwen/qwen-2.5-coder-32b-instruct:free` — Qwen 2.5 Coder 32B

### Mistral AI (Native API Key console.mistral.ai)
- `mistral-small-latest` — Mistral Small (24B Latest)
- `mistral-large-latest` — Mistral Large 2 (Flagship 128k)
- `codestral-latest` — Codestral Code Specialist

### OpenAI
- `gpt-4o-mini` — Fast multimodal
- `gpt-4o` — SOTA Vision + Reasoning
- `gpt-3.5-turbo` — Classic fast model

### Google / Meta / Groq (via OpenRouter & Groq API)
- `google/gemini-2.0-flash-exp:free` — Free next-gen Google model
- `meta-llama/llama-3.3-70b-instruct:free` — Free 70B Llama
- `llama-3.3-70b-versatile` — Ultra-fast Groq inference

---

## 📁 Project Structure

```
polymind-ai/
├── config/
│   ├── settings.py          → Django project settings
│   ├── urls.py              → Root URL routing (HTML + API)
│   └── template_views.py    → Frontend page views
│
├── users/
│   ├── models.py            → CustomUser with per-user API keys
│   ├── serializers.py       → Auth + Profile serializers
│   ├── views.py             → Register, Login, Profile, Logout
│   └── urls.py              → Auth URL routes
│
├── documents/
│   ├── models.py            → Document, ChatSession, ChatMessage
│   ├── ai_service.py        → LLM routing, RAG, Vision AI, embeddings
│   ├── views.py             → Upload, Ask, Summary, Sessions, Dashboard
│   ├── serializers.py       → API serializers
│   └── urls.py              → Document API routes
│
├── templates/
│   ├── base.html            → Base layout with JS helpers
│   └── pages/
│       ├── chat.html        → Main PolyMind AI Chat Interface
│       ├── auth.html        → Login / Register
│       ├── settings.html    → API Keys & Model Config
│       └── profile.html     → User Profile & Password
│
├── media/                   → Uploaded PDF files
├── chroma_db/               → Local ChromaDB vector store
├── manage.py
├── requirements.txt
└── .env
```

---

## 🔐 Environment Variables Reference

```env
# Django
SECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=*

# Provider API Keys (server-level fallbacks)
OPENROUTER_API_KEY=sk-or-v1-...        # Free Mistral 7B, Llama, Gemini
MISTRAL_API_KEY=...                     # Direct Mistral AI API
OPENAI_API_KEY=sk-...                   # OpenAI GPT-4o / Embeddings
GROQ_API_KEY=gsk_...                    # Groq ultra-fast inference
```

---

## 🎯 Resume Highlights

> **PolyMind AI** — Full-stack multi-model AI chat platform with:
> - **RAG pipeline** using LangChain + ChromaDB for intelligent PDF Q&A with source citations
> - **Multi-provider LLM routing** across Mistral AI (Tiny → Flagship), OpenAI GPT-4o, Gemini, and Groq
> - **Multimodal Vision AI** — real-time camera capture and image attachment with AI analysis
> - **Voice-to-text input** via Web Speech API with live waveform visualization
> - **JWT-secured REST API** with per-user API key management and token blacklisting
> - **Conversation history** with persistent sessions, export to Markdown, and quick prompt templates
> - Built with Django, DRF, LangChain, ChromaDB, Tailwind CSS, and Vanilla JS

---

## 📄 License

MIT License — Free to use, modify and distribute.
