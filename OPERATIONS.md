# Bright AEO Engine — Operations Guide

## What this system does

The AEO Engine measures how often Bright products are cited in AI model responses (Claude, GPT-4o, Gemini, Perplexity), benchmarks that visibility against competitors, generates prioritised recommendations to improve it, then produces channel-ready content and identifies customers for testimonial outreach and PR targets.

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- API keys for Anthropic, OpenAI, and Google (Perplexity optional)

---

## First-time setup

### 1. Clone / unpack the project

```
bright-aeo-engine/
├── backend/
│   ├── main.py          ← FastAPI server
│   ├── config.json      ← prompts, competitors, models
│   ├── agents/          ← query, analysis, content, targeting agents
│   ├── assets/          ← brand guidelines, product descriptions, customer proof
│   └── results/         ← run output files (auto-created)
├── frontend/
│   └── src/             ← React app
├── validate.py          ← pre-flight check
└── .env                 ← API keys (you create this)
```

### 2. Create your `.env` file

Create a file called `.env` in the project root (next to `validate.py`):

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...   # optional — skipped if blank
```

### 3. Install Python dependencies

```bash
cd bright-aeo-engine/backend
pip install -r requirements.txt
```

### 4. Install frontend dependencies

```bash
cd bright-aeo-engine/frontend
npm install
```

### 5. Run pre-flight validation

Before running anything, validate that all API keys work and models respond correctly:

```bash
cd bright-aeo-engine
python validate.py
```

You will see raw model responses, extracted brand mentions, and a cost estimate for a full run. If any model shows FAIL, check that key in `.env` before proceeding.

---

## Running the system

You need two terminal windows open simultaneously.

### Terminal 1 — Backend

```bash
cd bright-aeo-engine/backend
uvicorn main:app --reload --port 8000
```

The server starts at `http://localhost:8000`. If any required API key is missing, it will refuse to start with a clear error message.

### Terminal 2 — Frontend

```bash
cd bright-aeo-engine/frontend
npm run dev
```

The app opens at `http://localhost:5173`.

---

## Using the app

### Tab: Run

This is where you trigger a new analysis.

1. Click **Start new run**
2. Watch the live progress feed — each model/prompt combination streams in real time
3. When complete, you see a summary banner:
   - Overall citation rate for Bright
   - Number of prompts where Bright was cited
   - Watch-outs: topics or models where Bright has 0% citation rate (these need the most attention)
4. The run is saved automatically and appears in **Run history** below

You can filter a run to specific topics or models before starting (useful for quick checks or debugging).

### Tab: Insights

Select a completed run from the dropdown at the top. The page then shows:

**Summary cards** — top-line metrics: overall citation rate, total responses, models run, average competitor rate

**Trend chart** — citation rate over time by topic (requires at least 2 completed runs)

**Competitor rankings** — all brands ranked by citation rate. Bright is highlighted in blue. Red = competitors beating you. Green = competitors you are ahead of.

**Sentiment snippets** — the verbatim sentences from AI responses that mention Bright or competitors. Filter by brand or topic. These tell you the narrative the models are building — read them carefully.

**Recommendations** — Claude's prioritised AEO recommendations based on the analysis. Each card shows:
- Category (Content Gap, Narrative Risk, Technical, Domain Authority, Review Signal)
- Finding and recommended action
- Effort / Impact / Timeframe

  To act on a recommendation:
  1. Expand the card
  2. Select which channels you want content for (LinkedIn, Reddit, AccountingWEB, Wikipedia, G2, Trustpilot, PR pitch, web page)
  3. Click **Generate content**

**Content queue** — all generated content, grouped by recommendation. Each item shows the channel, status, and word count.

  To approve content:
  1. Click an item to expand it
  2. Edit the text if needed
  3. Enter your name in **Reviewer name**
  4. Click **Approve**

  **Reddit content requires an extra confirmation step.** After clicking Approve you will see a compliance acknowledgement you must confirm. This is enforced in the code — Reddit content cannot be approved without it.

**Targeting panel** — appears below each recommendation's content group after content has been generated. Two tabs:
- **Customer profile** — the ideal testimonial customer segment, CRM filter query, and a ready-to-use outreach email template
- **PR placements** — ranked outlets (AccountingWEB, TechRadar, etc.) with audience fit rating, draft pitch, and contact approach

### Tab: Config

Manage the inputs to the engine without touching JSON files.

**Prompts** — the search queries fired at each AI model. Add, edit, or delete prompts. Each prompt has a topic tag. Topics feed the trend chart and per-topic analysis.

**Competitors** — the peer set tracked in each analysis. Add or remove brands. Changes take effect on the next run.

**Models** — enable or disable individual AI models (Claude, GPT-4o, Gemini, Perplexity). Disable models you don't have keys for, or to reduce cost on quick checks.

---

## Cadence and workflow

### Weekly monitoring run
1. Open the app → Run tab → Start new run (all topics, all models)
2. Takes ~5–10 minutes depending on API latency
3. Go to Insights → check the trend chart for citation rate movement
4. Check watch-outs — any new 0% topics need immediate attention

### Monthly content sprint
1. Run a fresh analysis
2. Review Recommendations — work top to bottom by priority
3. For each recommendation, select channels and generate content
4. Review content, edit as needed, approve
5. Download/copy content from the queue and publish to channels
6. Check Targeting panel for that recommendation — run the CRM query and send testimonial outreach, send PR pitches

### Quarterly asset refresh
Update the brand assets in `backend/assets/` — these are injected into every content generation call:
- `brand-guidelines.md` — visual and messaging rules
- `tone-of-voice.md` — writing style
- `competitive-positioning.md` — how Bright differs from competitors
- `product-descriptions/` — one file per product (BrightPay Cloud, BrightTax, BrightAccountants, BrightManager)
- `customer-proof/case-studies.md` — customer stories referenced in content
- `customer-proof/stats.md` — proof points and statistics

---

## Run output files

Every run is saved to `backend/results/{run_id}.json`. These files contain the full raw data:

```
run_id, run_date, status
raw_results[]       ← every model response + extracted mentions
analysis{}          ← aggregated citation rates, by_topic, by_model, watchouts
recommendations{}   ← Claude's prioritised recommendations
content_items[]     ← all generated content with approval state
targeting_results[] ← customer profiles and PR placements
```

You can inspect these files directly if you need to export data or debug a run.

---

## Troubleshooting

**Backend won't start**
- Check `.env` exists in the project root and all three required keys are filled in (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY)
- Run `python validate.py` to pinpoint which key is failing

**Run starts but no results**
- Check the live feed for error messages — a model failing repeatedly will show red entries
- If >30% of queries fail, the run aborts. This usually means an API key is invalid or rate-limited.
- Check the backend terminal for stack traces

**Frontend shows nothing / can't connect**
- Make sure the backend is running on port 8000 before starting the frontend
- The Vite proxy routes `/runs`, `/config`, `/recommendations`, `/content`, `/targeting` to `localhost:8000`

**Perplexity queries are skipped**
- This is expected if `PERPLEXITY_API_KEY` is not set — the backend logs `INFO: PERPLEXITY_API_KEY not set`
- Add the key to `.env` and restart the backend

**Content generation fails for a recommendation**
- Make sure you have selected at least one channel before clicking Generate
- Check the backend terminal — the most common cause is the Claude API returning malformed JSON, which is automatically retried once

**Reddit content can't be approved without a name**
- This is intentional. The reviewer name field is required for Reddit. It is stored with the content as the accountability record.

---

## Cost estimates

Each full run (20 prompts × 4 models = 80 queries) costs approximately:

| Model | Est. cost per run |
|---|---|
| Claude (Opus 4.6) | ~$0.40–0.80 |
| GPT-4o | ~$0.20–0.40 |
| Gemini 1.5 Pro | ~$0.05–0.15 |
| Perplexity Sonar | ~$0.05–0.10 |
| **Total** | **~$0.70–1.45** |

Content generation (per recommendation, all 8 channels) adds ~$0.10–0.20 per call via Claude.

Run `python validate.py` for a live cost estimate based on current prompt lengths.
