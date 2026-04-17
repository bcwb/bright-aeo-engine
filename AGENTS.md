# Agent Architecture — Bright AEO Engine

This document describes every agent in `backend/agents/` and how they
interact during a run.

---

## Orchestration flow

```
Run triggered (POST /runs)
        │
        ▼
┌─────────────────┐
│   Orchestrator  │  builds job list, dispatches all queries in parallel
└────────┬────────┘
         │  one job per (prompt × model)
    ┌────┴────┬──────────┬────────────┐
    ▼         ▼          ▼            ▼
 Claude    OpenAI     Gemini    Perplexity     ← Query agents (run concurrently)
    └────┬────┴──────────┴────────────┘
         │  list[QueryResult]
         ▼
┌─────────────────┐
│    Analyser     │  pure Python, no API call — fast
└────────┬────────┘
         │  AnalysisOutput
         ▼
┌─────────────────┐
│  Recommender    │  one Claude API call
└────────┬────────┘
         │  RecommendationsOutput
         ▼
    Results saved to results/{run_id}.json
    SSE "complete" event sent to browser


Content generation triggered separately (POST /content)
        │
        ▼
┌──────────────────────────────────────────────────────┐
│  Content Agent  ×N  +  Targeting Agent ×2            │
│  (all parallel — one call per channel + 2 for        │
│   customer profile and PR placements)                │
└──────────────────────────────────────────────────────┘
         │
         ▼
    Appended to results/{run_id}.json
```

---

## Agent reference

### Orchestrator — `orchestrator.py`

**Role:** run coordinator. Nothing happens without it.

1. Reads active prompts and enabled models from config
2. Applies topic and model filters if set
3. Builds one `QueryJob` per (prompt × model) combination
4. Dispatches all jobs concurrently using `asyncio.gather`, with per-model
   semaphores (max 3 concurrent per model) and a 1-second inter-call delay
   to avoid rate limits
5. Tracks per-model failure rates — aborts only when *all* models exceed
   the 30% failure threshold (so one broken API key does not kill a healthy run)
6. Calls the Analyser synchronously once all queries are done
7. Calls the Recommender and handles failures gracefully (saves analysis
   even if recommendations fail)
8. Saves the full result payload to `results/{run_id}.json`
9. Emits SSE lifecycle events: `started`, `progress`, `analysing`,
   `recommending`, `complete`, `error`

**Has its own API call?** No — it coordinates other agents.

---

### Query agents — `query_claude.py`, `query_openai.py`, `query_gemini.py`, `query_perplexity.py`

**Role:** send a single prompt to one AI model and return the raw response.

Each agent:
- Sends the prompt exactly as written (no system prompt, no framing) so
  the AI responds as it would to a real user asking the question
- Records tokens used, latency, and any error
- Returns a `QueryResult` whether the call succeeds or fails — errors
  are captured and surfaced rather than raised, so one bad call does not
  stop the rest

| Agent | Model used |
|---|---|
| `query_claude.py` | `claude-opus-4-6` |
| `query_openai.py` | `gpt-4o` (or configured model) |
| `query_gemini.py` | `gemini-1.5-pro` (or configured model) |
| `query_perplexity.py` | `llama-3.1-sonar-large-128k-online` |

Perplexity is the most valuable for AEO purposes because it performs live
web search before answering — its responses reflect what is currently indexed
and cited on the web, not just training data.

**Has its own API call?** Yes — one call per job.

---

### Analyser — `analyser.py`

**Role:** extract structured citation data from raw query responses.
Pure Python — no API call.

For each response, it:
1. Builds a brand map from `config.brand_variants` and `config.peer_sets`,
   consolidating product name variants under canonical brand names
   (e.g. "BrightPay", "BrightPay Cloud", "Bright Payroll" all map to "Bright")
2. Scans each response for brand mentions using substring matching, recording
   the ordinal position (which brand was mentioned first, second, etc.)
   and extracting the sentence containing the mention as a sentiment snippet
3. Aggregates citation counts and rates overall, by topic, and by model
4. Calculates Bright's overall citation rate
5. Flags watch-outs: any topic or model where Bright received 0 citations

Output fields used downstream:
- `brand_citations` — overall rates used by Summary Cards and Competitor Rankings
- `by_topic` — per-topic rates used by Trend Chart and Recommendations
- `by_model` — per-model rates used by Summary Cards
- `bright_overall_rate` — stored on the run for the dropdown and trend chart
- `sentiment_snippets` — verbatim sentence extracts used by Sentiment Snippets
  panel and passed as context to Content Agent
- `watchouts` — shown in the run completion banner

**Has its own API call?** No.

---

### Recommender — `recommender.py`

**Role:** turn analysis data into prioritised, actionable recommendations.
One Claude API call per run.

Sends the full `AnalysisOutput` (serialised as JSON) to Claude Opus with
a specialist AEO system prompt that instructs it to:
- Work only from the topics and data present in the payload
- Name specific actions, not directions
- Prioritise by commercial impact
- Reference competitor names where they dominate a topic Bright should own
- Assign each recommendation to one of the 8 supported content channels

A scope constraint is appended to the user message when the run was filtered
to a specific topic, preventing Claude from generating recommendations about
products or topics not covered by the run.

Returns a ranked list of `Recommendation` objects (priority 1 = highest),
each with: category, topic, finding, action, effort, impact, timeframe,
and channels.

**Has its own API call?** Yes — one call (Claude Opus, max 8192 tokens).

---

### Content Agent — `content_agent.py`

**Role:** write channel-specific content for a recommendation.
One Claude API call per channel.

Triggered manually from the Insights tab after recommendations are reviewed.

For each requested channel:
1. Loads brand asset files from `backend/assets/`:
   - Always loaded: `tone-of-voice.md`, `competitive-positioning.md`,
     `customer-proof/stats.md`, `customer-proof/case-studies.md`
   - Topic-specific: the relevant product description file(s)
     (e.g. `product-descriptions/brightpay-cloud.md` for Payroll)
2. Combines the recommendation context, brand assets, and up to 5 sentiment
   snippets from the analysis into a single prompt
3. Calls Claude Opus with channel-specific writing instructions

Supported channels and what they produce:

| Channel | Output |
|---|---|
| `linkedin` | 150–300 word post, hook-first, one proof point, engagement question |
| `reddit` | Community post written as a peer, not a vendor — requires human review before posting |
| `wikipedia` | Neutral encyclopaedic section with verifiable facts only |
| `accountingweb` | 600–900 word contributed article, bureau-owner perspective |
| `g2_outreach` | 3-sentence customer outreach email requesting a G2 review |
| `trustpilot_outreach` | 3-sentence customer outreach email requesting a Trustpilot review |
| `pr_pitch` | Short PR pitch email with story angle, proof points, and a clear ask |
| `web_page` | 800–1200 word answer page targeting the specific prompt, with FAQ section |

Output quality scales directly with the content of the asset files.
Thin or placeholder assets produce generic output.

**Has its own API call?** Yes — one call per channel (Claude Opus, max 2048 tokens).

---

### Targeting Agent — `targeting_agent.py`

**Role:** generate outreach and PR strategy alongside content. Two Claude
API calls per content generation trigger (one per mode, run in parallel).

Triggered automatically whenever content is generated — the two targeting
calls run in parallel with the content calls.

**Mode: `customer_profile`**

Builds an ideal customer profile for testimonial and review outreach,
targeted to the specific gap identified in the recommendation. Output
includes:
- Product and company type to target
- Role titles to approach (e.g. "Payroll Bureau Manager", "Practice Partner")
- CRM filter query to identify the right customers in a CRM system
- Migration window — when in the customer lifecycle to reach out
- Outreach email template (ready to send, with `[REVIEW LINK]` placeholder)
- Review ask — the specific topics to request the customer mention
- Estimated pool size and expected yield

**Mode: `pr_placement`**

Scores a set of priority media outlets for the recommendation topic and
generates a tailored pitch for each. Output per outlet includes:
- Audience fit rating (High / Medium / Low) for UK/Ireland accountants
- Estimated lead time
- Pitch angle specific to the outlet's editorial focus
- Draft pitch email
- Contact approach

Current outlet list: AccountingWEB, TechRadar, startups.co.uk,
smallbusiness.co.uk, Reddit r/UKAccountants, Reddit r/payroll.

**Has its own API call?** Yes — two calls (Claude Opus) per content generation trigger.

---

## API call summary per full run

| Stage | Calls | Model |
|---|---|---|
| Query (8 prompts × 4 models) | ~32 | Claude, GPT-4o, Gemini, Perplexity |
| Analysis | 0 | — |
| Recommendations | 1 | Claude Opus |
| **Run total** | **~33** | |
| Content (per channel) | 1 per channel | Claude Opus |
| Customer profile | 1 | Claude Opus |
| PR placements | 1 | Claude Opus |
| **Per content trigger** | **8–10** | Claude Opus |
