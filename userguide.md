# Bright AEO Engine — User Guide

## 1. Overview

Bright AEO Engine measures Answer Engine Optimisation (AEO) visibility for Bright Software Group — specifically, how often Bright products are cited by AI models when accountants and payroll bureaux ask questions about software.

The tool works by sending a configurable set of search-intent prompts to multiple AI models simultaneously (Claude, GPT-4o, Gemini, Perplexity), then analysing the responses to determine:

- How often each Bright product is mentioned versus competitors
- Which topics and models have zero Bright citations (watch-outs)
- What specific language the models use when describing Bright and its competitors

From this analysis the engine generates a prioritised recommendations list and, from those recommendations, channel-specific content assets ready for review and deployment.

**Who it is for:** Bright Software Group internal marketing and product team members responsible for AEO strategy and content production.

---

## 2. How the engine works

The engine runs a five-stage pipeline: **Configure → Run → Analyse → Recommend → Generate**. Each stage feeds directly into the next.

---

### Stage 1 — Configure: build the lens

Before a run can happen, two things must be set up in the Configure tab: **prompts** and **peer sets**. Together these define the lens through which the engine reads AI responses.

**Prompts** are search-intent questions written to mimic how a real user would ask an AI assistant about software in your category. For example:

> "What is the best payroll software for UK accountants?"
> "Which payroll bureau software handles auto-enrolment?"

Prompts are grouped by **topic** (e.g. Payroll, Practice Management, Tax Compliance). The engine sends every active prompt to every enabled AI model — so if you have 10 prompts and 4 models, one run makes 40 API calls. Topics keep runs focused: you can run the full set or filter to a single topic.

**Peer sets** define who the engine looks for in each AI response. For the Payroll topic you might list Bright, Sage, Moneysoft, Iris, and Paychex, each with variant names that handle different ways the brand appears in text (e.g. "BrightPay", "Bright Pay", "brightpay.co.uk" all map to the same brand). The peer set is the competitive lens — it determines who appears in the rankings, not just whether Bright is mentioned.

The **benchmark brand** (set in the Configure tab) is the brand whose citation rate is highlighted throughout the tool — summary cards, trend chart, run names, watch-outs. It defaults to Bright but can be changed if the tool is used for a different brand.

---

### Stage 2 — Run: dispatch jobs and collect responses

When you trigger a run the engine constructs one **job** per prompt/model combination and dispatches all jobs simultaneously. Each job sends the prompt text to the relevant AI model API and waits for the response.

Jobs run in parallel with a small rate-limiting delay per model to avoid hitting API quotas. Progress is streamed live to the browser via Server-Sent Events — you see each response arrive in real time with the model name, topic, running cost, and whether the benchmark brand was mentioned.

The engine only aborts if every active model is failing above a 30% error rate. One model going down (e.g. an OpenAI quota limit) does not stop a run where the other models are healthy — those jobs continue and their results are saved.

---

### Stage 3 — Analyse: read responses through the peer lens

Once all responses are collected, the analysis agent reads each response and scans it for mentions of every brand in every peer set, using the full list of variant names.

For each brand, per topic, per model, it records:
- Whether the brand was mentioned at least once
- The verbatim sentences in which the brand was mentioned (sentiment snippets)

From this it calculates:
- **Citation rate** — the percentage of responses in which a brand was mentioned at least once
- **By-topic breakdown** — citation rates per brand per topic, so you can see where Bright is strong and where it is absent
- **Watch-outs** — any topic/model combination where the benchmark brand citation rate is zero, meaning the AI never mentioned Bright when asked about that topic

All of this becomes the **Insights** view. The summary cards show the overall benchmark citation rate and watch-out count. The competitor rankings show every brand's citation rate within each topic peer set. The sentiment snippets show the exact language the models used — useful for understanding how AI currently describes your brand versus competitors.

The trend chart plots citation rates across all saved runs chronologically, so you can track whether your AEO actions are improving visibility over time.

---

### Stage 4 — Recommend: turn the analysis into a prioritised action list

After analysis, the engine calls the recommendations agent (Claude). It reads the full analysis — citation rates, competitive rankings, watch-outs, and sentiment snippets — and produces a prioritised list of recommended actions.

Each recommendation includes:
- What the analysis found (the gap or risk)
- The specific action to take
- Effort, impact, and timeframe ratings
- Which content channels would be most effective for that action

The recommendations are scoped strictly to the topics and data present in the run — the agent is instructed not to reference topics or brands that were not part of the analysis.

---

### Stage 5 — Generate: produce content grounded in brand context

When you generate content for a recommendation, the engine loads two sets of context files before calling Claude:

**Core assets** (always loaded, regardless of topic):

| File | What it provides |
|---|---|
| `assets/tone-of-voice.md` | Bright's writing style, vocabulary preferences, tone guidelines |
| `assets/brand-guidelines.md` | Colour, typography, logo rules, messaging pillars |
| `assets/competitive-positioning.md` | How Bright differentiates from each competitor |
| `assets/customer-proof/stats.md` | Verified proof points with numbers (e.g. "saves 63 hours a month") |
| `assets/customer-proof/case-studies.md` | Customer stories and outcomes |

**Topic asset** (one file per topic, loaded dynamically):

| File | What it provides |
|---|---|
| `assets/product-descriptions/{topic_key}.md` | Product detail, features, ideal customer profile, and differentiators specific to this topic |

Claude receives all six files as context alongside the recommendation details, the target channel, and the sentiment snippets from the run. It generates content that is grounded in Bright's actual brand voice, competitive positioning, and verified proof points — not generic AI copy.

**This is why asset file quality matters so much.** Empty or placeholder files produce generic output. Populated files with specific statistics, real differentiators, and Bright's tone produce content that is ready to review and deploy. Populating the topic asset files for your highest-priority topics is the single most effective action for improving content quality.

The content agent runs all requested channels in parallel and saves each item to the run's result file. Reddit content is always flagged for human review before use.

---

## 3. Prerequisites

### Runtime

| Requirement | Minimum version |
|---|---|
| Python | 3.11 |
| Node.js | 18 |

### API keys

Three API keys are required. The application will refuse to start if any are missing.

| Key | Provider | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Yes |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Yes |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | Yes |
| `PERPLEXITY_API_KEY` | [docs.perplexity.ai](https://docs.perplexity.ai) | No — Perplexity queries are skipped if absent |

---

## 4. Installation

### Clone the repository

```bash
git clone <repository-url> bright-aeo-engine
cd bright-aeo-engine
```

### Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Install frontend dependencies

```bash
cd ../frontend
npm install
```

### Configure environment variables

Create a `.env` file in the project root (alongside `backend/` and `frontend/`):

```bash
# bright-aeo-engine/.env

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...   # optional

# Optional logging config
LOG_LEVEL=INFO                 # DEBUG | INFO | WARNING | ERROR (default: INFO)
LOG_FORMAT=dev                 # dev | json (default: dev)
```

The backend loads this file automatically via `python-dotenv` on startup.

---

## 5. Starting the application

### Start the backend

Open a terminal in the `backend/` directory:

```bash
cd bright-aeo-engine/backend
uvicorn main:app --reload --port 8000
```

The `--reload` flag watches for file changes and restarts the server automatically — no manual restart needed during development.

The API is available at `http://localhost:8000`. Interactive API documentation is at `http://localhost:8000/docs`.

**If port 8000 is already in use:**

```bash
lsof -ti:8000 | xargs kill -9
```

Then start the backend again.

### Start the frontend

Open a second terminal in the `frontend/` directory:

```bash
cd bright-aeo-engine/frontend
npm run dev
```

The application is available at `http://localhost:5173`.

Vite proxies API calls from the frontend to the backend automatically — no CORS configuration is required during development. The proxy covers `/runs`, `/config`, `/recommendations`, `/content`, `/targeting`, `/assets`, and `/logs`.

---

## 6. Configure tab

The Configure tab is the starting point for a new installation or when the scope of the analysis needs to change. Access it from the sidebar navigation.

### Prompts

Prompts are the search-intent questions sent to each AI model. They are grouped by topic. The engine sends every active prompt to every enabled model, so the total number of API calls for a run is: `active prompts × enabled models`.

**What makes a good prompt:** Prompts should reflect how a real user would ask an AI assistant about software in your category. Use natural language, include relevant qualifiers (UK, bureau, accountants), and include both broad category prompts and comparison-style prompts (e.g. "BrightPay alternative").

**Topic cards** are collapsed by default. Click a topic header to expand it and see its prompts and competitor peer set side by side.

**To add a prompt within an existing topic:**
1. Expand the topic card.
2. Use the add row at the bottom of the Prompts table within that card.
3. Enter the prompt text. The topic is set automatically from the card context.
4. Click Add.

**To add a prompt for a new topic:**
1. Use the standalone add row below all topic cards.
2. Enter both the topic name and prompt text.
3. Click Add. The new topic card, its peer set, and its topic asset file are all created automatically.

**To toggle a prompt active/inactive:** Click the toggle switch in the prompt row. Inactive prompts are not sent during runs.

**To edit a prompt:** Click the text in the prompt row to edit it inline.

**To delete a prompt:** Click the delete button (trash icon) in the prompt row.

### Competitors and peer sets

Each topic has one competitor peer set — the list of brands the analysis will look for in AI responses. The peer set determines who appears in the competitor rankings in the Insights tab.

**To add a competitor:**
1. Expand the topic card.
2. Use the add row at the bottom of the Competitor Peer Set table.
3. Enter the competitor name.
4. Optionally add variant names (alternative spellings, domain names, product names) — these are all treated as the same brand in citation counting.

**Variant names matter.** If a brand appears in AI responses as "Sage Payroll" and "Sage", both variants must be listed or only exact matches are counted. The Bright peer set entry, for example, includes "Bright", "BrightPay", "brightpay.co.uk", and "brightsg.com".

**To delete a competitor:** Click the delete button in the competitor row.

**To delete a peer set:** Click the delete button on the topic card header. This also removes all competitors in that peer set. The topic's prompts are not affected.

### Models

The Models section shows the four supported AI models with enable/disable toggles:

| Model key | Underlying model |
|---|---|
| `claude` | claude-opus-4-6 |
| `openai` | gpt-4o |
| `gemini` | gemini-1.5-pro |
| `perplexity` | llama-3.1-sonar-large-128k-online |

Disabling a model excludes it from future runs but does not affect previous results. Perplexity can only be enabled if `PERPLEXITY_API_KEY` is set in `.env`.

### Benchmark brand

The benchmark brand is the brand whose citation rate is shown prominently throughout the Insights tab, in summary cards, trend charts, watch-outs, and run names.

**To change the benchmark brand:**
1. In the Benchmark Brand section, click Change.
2. Select from the dropdown (populated from `brand_variants` keys in config) or type a name.
3. Click Save.

The brand must have an entry in `brand_variants` in `config.json` to be detected in AI responses. The default is "Bright".

### Brand assets

Asset files provide context to the content generation agent. The Configure tab lists all asset files with an Open button that opens the file in your default editor (macOS only).

**Core assets** are loaded for every content generation request, regardless of topic:

| File | Purpose |
|---|---|
| `backend/assets/tone-of-voice.md` | Writing style and voice guidelines |
| `backend/assets/brand-guidelines.md` | Brand colour, typography, logo rules |
| `backend/assets/competitive-positioning.md` | Differentiators vs competitors |
| `backend/assets/customer-proof/stats.md` | Verified proof points with numbers |
| `backend/assets/customer-proof/case-studies.md` | Customer stories |

**Topic assets** are loaded alongside core assets when generating content for a specific topic. Each topic gets one file, auto-created at `backend/assets/product-descriptions/{topic_key}.md`.

Content quality scales directly with asset file quality. Placeholder assets produce generic output. Populating these files — particularly with specific product features, verified statistics, and competitive differentiators — is the highest-leverage action for improving generated content.

---

## 7. Running an analysis

Navigate to the Run tab.

### Filters

Before triggering a run you can optionally narrow its scope:

- **Topic filter** — run prompts for one topic only, or All topics (default).
- **Model filter** — query one model only, or All enabled models (default).

The estimated call count shown below the filters updates as you change selections: `active prompts matching topic × enabled models matching model filter`.

### Triggering a run

Click **Run Analysis**. The button text changes to show the current phase:

- **Querying models…** — prompts are being sent to AI models.
- **Analysing…** — responses have been collected and citation analysis is running.
- **Generating recommendations…** — the recommender agent (Claude) is producing the prioritised action list. This phase typically takes 20–40 seconds.

The run fires asynchronously. The page does not need to stay open for the run to complete, but the live feed will stop updating if you navigate away.

### Live feed

The Live Feed shows progress events as they arrive via Server-Sent Events:

- Each row represents one completed query (prompt + model combination).
- The row shows the model, topic, whether the benchmark brand was cited, and the running API cost in USD.
- A progress bar shows queries completed out of total.
- Watch-out banners appear in orange when the benchmark brand citation rate for a topic/model is zero.

### Cost estimate

The running API cost is shown in the progress bar area during a run and in the summary banner after completion. Costs are estimated based on token usage reported by each model's API.

### Abort threshold behaviour

The run will not abort if one model starts failing (for example, if an OpenAI quota is exceeded). The orchestrator only aborts when **all** active models exceed a 30% failure rate. If a single model is struggling, its queries return `status='error'` but the run continues with the other models. Failed calls are counted in the run summary.

### After a run completes

A summary banner shows:
- Benchmark brand overall citation rate
- Total responses collected
- Number of recommendations generated
- Estimated total cost
- Run duration in seconds
- Watch-outs (topics/models with zero benchmark brand citations)

The app automatically navigates to the Insights tab with the completed run selected.

---

## 8. Insights tab

### Selecting a run

Use the dropdown at the top right to select any previous run. Run names follow the format:

```
{date} — {scope} — {citation rate}
```

For example: `2026-04-17 — Payroll — 45% cited`

If multiple runs share the same date and scope, a version suffix is added: `v1`, `v2`, etc., assigned in chronological order (v1 = earliest).

When a run completes the app navigates here automatically with the new run pre-selected.

### Summary cards

Four cards show the key metrics for the selected run:

- **Citation rate** — percentage of responses in which the benchmark brand was mentioned at least once.
- **Total responses** — number of successful model responses collected.
- **Failed calls** — number of API calls that returned an error.
- **Watch-outs** — number of topic/model combinations where the benchmark brand citation rate is zero.

### Trend chart

The trend chart plots the benchmark brand citation rate across all saved runs, grouped by topic. Use this to track whether AEO actions are improving visibility over time. Each line represents one topic; points are connected in chronological order.

### Competitor rankings

Shows each brand's citation rate within each topic peer set, sorted by rate descending. The benchmark brand's row is highlighted. This view shows directly where the benchmark brand ranks relative to competitors for each topic.

### Sentiment snippets

Verbatim sentences from AI responses that contain a brand mention. Snippets are grouped by brand. The section starts collapsed — click to expand. Snippets show the actual language models use when describing each brand, which is useful input for content strategy.

### Content queue

Shows all content items that have been generated for this run. Each item shows the channel, word count, status (draft / approved), and the recommendation it was generated from. See section 8 for how to generate new content.

---

## 9. Generating content

Content is generated from the recommendations produced after each run.

### The recommendations list

Recommendations are listed in the Insights tab below the Competitor Rankings section. Each recommendation shows:

- **Priority** — numbered from 1 (highest) downward.
- **Category** — one of: Content Gap, Narrative Risk, Technical, Domain Authority, Review Signal.
- **Topic** — which analysis topic the recommendation addresses.
- **Finding** — what the analysis revealed.
- **Action** — the specific action recommended.
- **Effort / Impact / Timeframe** — Low/Medium/High ratings and a suggested timeframe.
- **Suggested channels** — which content channels the recommender suggests for this action.

### Selecting channels and triggering generation

On a recommendation card, click **Generate Content**. A channel selector appears showing the eight available channels. You can select multiple channels; content is generated for all selected channels in parallel.

| Channel | What is generated |
|---|---|
| `linkedin` | LinkedIn post in Bright tone of voice |
| `reddit` | Reddit comment or post — **always requires human review** |
| `wikipedia` | Draft Wikipedia section or article contribution |
| `accountingweb` | Article or comment for AccountingWeb community |
| `g2_outreach` | Outreach message to encourage G2 reviews |
| `trustpilot_outreach` | Outreach message to encourage Trustpilot reviews |
| `pr_pitch` | PR pitch letter to a relevant journalist or outlet |
| `web_page` | Web page copy for Bright's website |

Generation typically takes 10–30 seconds per channel (all channels run in parallel).

### Human review for Reddit

Reddit content always has `human_review_required: true`. This is a hardcoded safety measure — Reddit is a sensitive channel and auto-posting AI-generated content without review would violate community guidelines and could damage brand reputation.

To approve Reddit content (and any other content item):
1. Open the content item in the Content Queue.
2. Review the text and edit as needed.
3. Enter your name in the reviewer field.
4. Click Approve.

Approved items record the reviewer's name and the approval date.

### Targeting panel

Alongside content generation, the engine produces targeting output for each recommendation:

- **Customer profile** — role titles, company type, company size range, a plain-English CRM query, an outreach email template, and a review request template.
- **PR placement recommendations** — suggested outlets with pitch angle, draft pitch copy, and contact approach.

These are shown in the Targeting section of each recommendation card.

---

## 10. Monitor tab

The Monitor tab shows a live log stream of backend activity — run lifecycle events, AI calls, config changes, and errors.

### Summary cards

Four cards at the top show event counts by level from the current buffer:

- **Errors** — highlighted red if count is greater than zero.
- **Warnings**
- **Info events**
- **Debug events**

### Level filter

Click a level button (ALL, ERROR, WARNING, INFO, DEBUG) to filter the log table. The summary cards always show counts for the full buffer regardless of the active filter.

### Auto-refresh

Auto-refresh is on by default and polls for new events every 5 seconds. Toggle it off to freeze the display for closer inspection. A manual Refresh button is also available.

The last refresh timestamp is shown below the controls.

### Expanding context

Each log row shows the level, timestamp, source module name, event message, and up to two context key=value pills. Click a row to expand it and see all context fields (for example, a run event will show `run_id`, `topic_filter`, `model_filter`; a config change event will show `change_type`, `entity_id`, `topic`).

Error and Critical rows have a red background to make them visible at a glance.

### Clearing the buffer

Click **Clear buffer** and confirm to remove all events from the in-memory log buffer. This does not affect any files on disk or any log aggregator output. The buffer holds a maximum of 500 events; oldest events are dropped automatically when full.

---

## 11. Adding a new AI model

The agent registry is designed so that adding a new AI model requires exactly two steps and no changes to the orchestrator.

### Step 1: Create the agent file

Create `backend/agents/query_<modelname>.py`. The file must implement one async function:

```python
async def query(job: QueryJob) -> QueryResult:
    """
    Execute a single AI query job.

    Must return a QueryResult with status='success' or status='error'.
    Must never raise — catch all exceptions and return status='error'.
    """
    ...
```

The function receives a `QueryJob` (from `backend/models.py`) with `job_id`, `prompt`, `topic`, `model`, and `peer_set`. It must return a `QueryResult` with at minimum `status`, `response_text`, `tokens_used`, and `latency_ms`. On any exception, catch it and return `status='error'` with the error message — agents must never raise to the caller.

### Step 2: Register the agent

At the bottom of the new file, call `register()`:

```python
import sys
from agents.registry import register

register(
    name="mymodel",           # must match the key used in config.json models
    env_key="MYMODEL_API_KEY",  # environment variable holding the API key
    cost_per_token=0.000005,  # approximate USD per input token (for cost estimation)
    module=sys.modules[__name__],
)
```

### Step 3: Add the model to config.json

Add an entry to the `models` object in `backend/config.json`:

```json
"models": {
  "mymodel": {
    "enabled": true,
    "model_string": "my-model-id-v1"
  }
}
```

That is all. On the next server start the orchestrator will discover the new model via `registry.get_active()` and include it in runs. The new model will appear in the Run tab's Model filter dropdown.

---

## 12. Troubleshooting

### Backend not responding

Check whether port 8000 is already in use:

```bash
lsof -ti:8000
```

If a process is listed, kill it and restart the backend:

```bash
lsof -ti:8000 | xargs kill -9
uvicorn main:app --reload --port 8000
```

### API 404 on a new route

If you have added a new API route and the frontend returns 404, check `frontend/vite.config.js`. Every API path prefix must be listed in the Vite proxy configuration, otherwise Vite will not forward the request to the backend.

### Recommendations cross-contaminating topics

If the recommender lists recommendations for topics that were not in the run (for example, mentioning BrightManager visibility in a Payroll-only run), check that the recommender's system prompt does not include a hardcoded product list. The product list was removed deliberately to prevent this contamination. Do not add it back.

### Content generation errors

If content generation fails with a channel error, check that the channel name is in the valid set of eight: `linkedin`, `reddit`, `wikipedia`, `accountingweb`, `g2_outreach`, `trustpilot_outreach`, `pr_pitch`, `web_page`. Channel normalisation in `ContentService._normalise_channel()` handles common variants, but completely unrecognised channel names are silently dropped.

### Trend chart empty

If the Insights trend chart shows no data, verify that `by_topic` is present in the `GET /runs` response (open the browser developer tools Network tab and inspect the response). If it is absent, the backend was not restarted after the `by_topic` field was added to `RunService.list_runs()`. Restart the backend.

### New topic has no asset file

If a newly created topic shows a warning "No asset file — reload to create" in the Configure tab's Brand Assets section, call `GET /config` to trigger `_ensure_topic_assets`. In practice, navigating to the Configure tab is sufficient as it calls `GET /config` on mount. Check `backend/assets/product-descriptions/` for the generated file.

### Missing API key error on startup

The backend validates `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and `GOOGLE_API_KEY` on startup and raises a `RuntimeError` listing any missing keys. Check `bright-aeo-engine/.env` and ensure all three keys are present. The `.env` file must be in the project root, not inside `backend/`.

---

## 13. Environment variables reference

All variables are set in `bright-aeo-engine/.env` in the project root.

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key. Used for Claude query agent, recommender, content agent, and targeting agent. |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key. Used for GPT-4o query agent. |
| `GOOGLE_API_KEY` | Yes | — | Google API key. Used for Gemini query agent. |
| `PERPLEXITY_API_KEY` | No | — | Perplexity API key. If absent, Perplexity queries are skipped and the model is ignored even if enabled in config. |
| `LOG_LEVEL` | No | `INFO` | Minimum log level written to stdout and captured in the in-memory buffer. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `LOG_FORMAT` | No | `dev` | Log output format. `dev` produces coloured, human-readable output. `json` produces one JSON object per line, suitable for log aggregators such as Datadog or CloudWatch. |
