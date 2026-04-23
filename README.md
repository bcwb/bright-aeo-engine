# Bright AEO Engine

An internal tool for Bright Software Group that measures and improves **Answer Engine Optimisation (AEO)** visibility — how often Bright products are cited by AI models when accountants and payroll bureaux ask questions about software.

The engine sends configurable search-intent prompts to Claude, GPT-4o, Gemini, and Perplexity simultaneously, analyses brand citation rates against a configurable competitor peer set, generates a prioritised recommendations list, and produces channel-specific content assets ready for review and deployment.

**For:** Bright Software Group internal marketing and product team.

---

## User Guide

Full usage instructions, workflow walkthrough, and troubleshooting are in **[userguide.md](userguide.md)**.

---

## Prerequisites

| Requirement | Minimum version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

You will also need API keys for:

| Service | Key name | Where to get it |
|---|---|---|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | console.anthropic.com |
| OpenAI (GPT-4o) | `OPENAI_API_KEY` | platform.openai.com |
| Google (Gemini) | `GOOGLE_API_KEY` | aistudio.google.com |
| Perplexity | `PERPLEXITY_API_KEY` | perplexity.ai/settings/api |

The app will refuse to start if any key is missing. You can disable individual models in the Configure tab once the app is running.

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/bcwb/bright-aeo-engine.git
cd bright-aeo-engine
```

**2. Run the install script**

```bash
bash install.sh
```

This will:
- Check Python and Node.js are installed
- Create a Python virtual environment in `backend/venv/`
- Install all Python and Node dependencies
- Create a `.env` file from the template

**3. Add your API keys**

Open `.env` and fill in your four API keys:

```
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
PERPLEXITY_API_KEY=your-key-here
```

---

## Running the app

Open two terminals from the project root.

**Terminal 1 — Backend**

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend**

```bash
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## Dependencies

### Backend (Python)

| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn[standard]` | ASGI server |
| `anthropic` | Claude API client |
| `openai` | GPT-4o API client |
| `google-genai` | Gemini API client |
| `requests` / `httpx` | HTTP clients (Perplexity + async) |
| `python-dotenv` | Loads `.env` at startup |

### Frontend (Node)

| Package | Purpose |
|---|---|
| React 18 | UI framework |
| Vite | Dev server and bundler |
| Tailwind CSS | Styling |
| Recharts | Citation rate charts |

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python), async, MVC architecture |
| Frontend | React 18, Vite, Tailwind CSS |
| Live updates | Server-Sent Events (SSE) |
| Storage | JSON files — no database required |
| AI models | Claude Opus 4.6, GPT-4o, Gemini 1.5 Pro, Perplexity |

---

*© 2026 Bright. All Rights Reserved. — Simply Brilliant Software*
