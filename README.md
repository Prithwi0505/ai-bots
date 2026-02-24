# Integrated Bots – FastAPI Backend

A multi-bot AI system powered by **Google Gemini**. It routes user queries to 5 specialized bots via a hybrid classifier (rule-based + LLM). Built with **FastAPI** for a clean REST API.

---

## 🤖 Bots Overview

### 🏦 Banking Bot
- **Purpose:** Answers banking FAQs (KYC, loans, cards, interest rates, fees).
- **Safety Rule:** Any query about personal data (`"my balance"`, `"my account"`, `"my card"`, `"my transaction"`, `"my loan"`) returns `"Authentication required."` — never exposes personal info.
- **Endpoint:** `POST /banking`

### 🍳 Cooking Bot
- **Purpose:** Generates structured recipes with **Ingredients**, **Steps**, and **Cooking Time**.
- **Safety Rule:** Requires at least 2 words in the query. Single-word queries get a fallback: `"Please tell me the main ingredient or dish you want a recipe for..."`.
- **Endpoint:** `POST /cooking`

### 💰 Finance Bot
- **Purpose:** Provides educational explanations about finance topics.
- **Safety Rule:** Never gives financial advice. Every response **must** end with: `"Disclaimer: This is educational information only, not financial advice."` — auto-appended if missing.
- **Endpoint:** `POST /finance`

### 🧠 GPT Master Bot
- **Purpose:** AI mentor that provides step-by-step guidance and explanations.
- **Safety Rule:** Always admits uncertainty rather than guessing. Focuses on clear, structured teaching.
- **Endpoint:** `POST /gpt_master`

### 🎥 GenZ Content Bot
- **Purpose:** Generates social media content (reels, scripts, captions, threads) in GenZ style.
- **Features:**
  - Internal sub-classifier detects content type automatically
  - Language detection (auto or manual)
  - External API integrations: **NewsAPI** (trending), **TMDB** (movies), **Wikipedia** (facts)
  - Platform-specific formatting (Instagram, TikTok, YouTube, LinkedIn, X, WhatsApp)
  - Optional camera cues, trending suggestions, reel comparisons
- **Endpoints:** `POST /genz` (simple) and `POST /genz/detailed` (full params)

### 🔀 Auto-Router / Classifier
- **Purpose:** Automatically routes any query to the right bot.
- **How it works:**
  1. **Rule-based keyword matching** (fast, no API call)
  2. If no keyword match → **Gemini LLM classification** (slower, more accurate)
  3. If LLM fails → **Falls back to Finance bot** (safe default)
- **Endpoints:** `POST /chat` (routes + gets response) and `POST /classify` (classification only)

---

## 📁 Project Structure

```
fastApi_version/
├── main.py              # FastAPI app entry point
├── config.py            # Loads .env, defines API keys and constants
├── gemini_helpers.py    # Shared Gemini API client with model fallback
├── schemas.py           # Pydantic request/response models
├── requirements.txt     # Python dependencies
├── .env.example         # Template for API keys
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── static/
│   └── index.html       # Test frontend UI
└── routers/
    ├── __init__.py
    ├── banking.py       # Banking bot endpoint
    ├── cooking.py       # Cooking bot endpoint
    ├── finance.py       # Finance bot endpoint
    ├── gpt_master.py    # GPT Master bot endpoint
    ├── genz.py          # GenZ bot endpoints
    └── classifier.py    # Auto-router + classifier endpoints
```

---

## 🚀 Setup & Run

### 1. Clone / Copy

Copy the entire `fastApi_version/` folder to any machine.

### 2. Create `.env`

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here     # Required — get from https://aistudio.google.com/app/apikey
NEWS_API_KEY=your_newsapi_key_here           # Optional — for GenZ trending content
TMDB_API_KEY=your_tmdb_api_key_here          # Optional — for GenZ movie content
```

> **Note:** `GEMINI_API_KEY` is required. Without it, the server won't start. The other two are optional — the GenZ bot works without them, but trending/movie features will be limited.

### 3. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **Windows (CMD):** `.\.venv\Scripts\activate.bat`
- **Linux/Mac:** `source .venv/bin/activate`

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 🧪 Testing the Bots

### Option A: Web UI (easiest)

Open **http://localhost:8000/ui** in your browser. You'll see a tabbed interface where you can test every bot by typing a query and clicking Send.

### Option B: Swagger Docs (interactive API docs)

Open **http://localhost:8000/docs** — FastAPI auto-generates interactive docs. Click any endpoint → "Try it out" → paste a JSON body → "Execute".

### Option C: Command Line (curl / PowerShell)

> **PowerShell users:** Use `Invoke-RestMethod` instead of `curl`.

---

#### Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

---

#### 🏦 Banking Bot
```bash
# Normal question
curl -X POST http://localhost:8000/banking \
  -H "Content-Type: application/json" \
  -d '{"query": "What documents are needed for KYC?"}'

# Auth trigger test (should return "Authentication required.")
curl -X POST http://localhost:8000/banking \
  -H "Content-Type: application/json" \
  -d '{"query": "Show my balance"}'
```

**Expected responses:**
- Normal → `{"bot":"banking", "reply":"...KYC answer..."}`
- Auth trigger → `{"bot":"banking", "reply":"Authentication required."}`

---

#### 🍳 Cooking Bot
```bash
# Recipe request
curl -X POST http://localhost:8000/cooking \
  -H "Content-Type: application/json" \
  -d '{"query": "chicken biryani recipe"}'

# Fallback test (too short)
curl -X POST http://localhost:8000/cooking \
  -H "Content-Type: application/json" \
  -d '{"query": "eggs"}'
```

**Expected responses:**
- Recipe → structured output with **Ingredients**, **Steps**, **Cooking Time**
- Fallback → `"Please tell me the main ingredient or dish you want a recipe for..."`

---

#### 💰 Finance Bot
```bash
curl -X POST http://localhost:8000/finance \
  -H "Content-Type: application/json" \
  -d '{"query": "What is compound interest?"}'
```

**Expected:** Educational explanation ending with `"Disclaimer: This is educational information only, not financial advice."`

---

#### 🧠 GPT Master Bot
```bash
curl -X POST http://localhost:8000/gpt_master \
  -H "Content-Type: application/json" \
  -d '{"query": "Help me plan my AI learning path"}'
```

**Expected:** Step-by-step mentoring response.

---

#### 🎥 GenZ Bot (Simple)
```bash
curl -X POST http://localhost:8000/genz \
  -H "Content-Type: application/json" \
  -d '{"query": "Create an Instagram reel script for a fitness page"}'
```

**Expected:** GenZ-style content with hashtags and CTA.

---

#### 🎥 GenZ Bot (Detailed)
```bash
curl -X POST http://localhost:8000/genz/detailed \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Indian street food vlog",
    "platform": "instagram_reel",
    "duration": 45,
    "content_type": "script_voiceover",
    "area_spec": "pani puri",
    "location": "Mumbai",
    "language": "en",
    "include_trending": true,
    "deliver_camera_cues": true,
    "compare_with_reels": true
  }'
```

**Detailed parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | Content topic |
| `platform` | string | `"instagram_reel"` | Target platform (`instagram_reel`, `tiktok`, `youtube_short`, `linkedin_post`, `x_thread`, `whatsapp_status`) |
| `duration` | int | `30` | Video length in seconds (5–120) |
| `content_type` | string | `"script_voiceover"` | Format (`script_voiceover`, `dialogue`, `listicle`, `tutorial`, `comedy_sketch`) |
| `area_spec` | string | `""` | Specific focus/niche |
| `location` | string | `""` | Location context |
| `language` | string | `"auto"` | Language code or `"auto"` for detection |
| `include_trending` | bool | `true` | Include trending topics from NewsAPI/TMDB |
| `deliver_camera_cues` | bool | `true` | Include camera angle/shot instructions |
| `compare_with_reels` | bool | `true` | Include suggestions comparing to popular reels |

---

#### 🔀 Auto-Router (`/chat`)
```bash
# Routes automatically to the right bot
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How to make pancakes"}'
```

**Expected:** `{"bot":"cooking", "reply":"...", "routed_to":"cooking"}`

Test different queries to verify routing:

| Query | Expected `routed_to` |
|-------|---------------------|
| `"How to make pancakes"` | `cooking` |
| `"What is EMI on credit cards?"` | `banking` |
| `"Explain diversification"` | `finance` |
| `"Instagram reel for startup"` | `genz` |
| `"Explain this code step by step"` | `gpt_master` |

---

#### 🏷️ Classifier Only (`/classify`)
```bash
# Rule-based (fast, no API call)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"query": "How to make pasta", "use_llm": false}'

# LLM-based (slower, higher accuracy)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"query": "How to make pasta", "use_llm": true}'
```

**Expected:**
- Rule-based → `{"category":"cooking", "bot":"cooking", "confidence":"medium"}`
- LLM-based → `{"category":"cooking", "bot":"cooking", "confidence":"high"}`

---

## 📋 All Endpoints Summary

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|-------------|
| `GET` | `/` | Health check + info | — |
| `GET` | `/health` | Simple health check | — |
| `GET` | `/ui` | Test frontend UI | — |
| `GET` | `/docs` | Swagger API docs | — |
| `POST` | `/chat` | Auto-routed chat | `{"query": "..."}` |
| `POST` | `/classify` | Classification only | `{"query": "...", "use_llm": false}` |
| `POST` | `/banking` | Banking bot | `{"query": "..."}` |
| `POST` | `/cooking` | Cooking bot | `{"query": "..."}` |
| `POST` | `/finance` | Finance bot | `{"query": "..."}` |
| `POST` | `/gpt_master` | GPT Master bot | `{"query": "..."}` |
| `POST` | `/genz` | GenZ bot (simple) | `{"query": "..."}` |
| `POST` | `/genz/detailed` | GenZ bot (full params) | See detailed params above |

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **FastAPI** — REST API framework
- **Google Gemini** (`google-genai`) — AI model (gemini-2.5-pro → flash → flash-lite fallback)
- **Pydantic v2** — Request/response validation
- **Uvicorn** — ASGI server
- **langdetect** — Language detection (GenZ bot)
- **requests** — External API calls (NewsAPI, TMDB, Wikipedia)

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `GEMINI_API_KEY missing` | Create `.env` file from `.env.example` and add your key |
| `403 PERMISSION_DENIED` | API key is invalid/expired — generate a new one at [AI Studio](https://aistudio.google.com/app/apikey) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the activated venv |
| `Connection refused` | Server isn't running — start with `uvicorn main:app --reload --port 8000` |
| Slow responses | Normal — Gemini API takes 2–15 seconds. The fallback chain tries up to 3 models |
| Empty responses | All 3 Gemini models failed — check API key and quota |
