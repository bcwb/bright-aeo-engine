# Bright AEO Engine — Release Notes

Bright AEO Engine is an internal tool for Bright Software Group that measures and improves Answer Engine Optimisation (AEO) visibility — how often Bright products are cited by AI models (Claude, GPT-4o, Gemini, Perplexity) when accountants and payroll bureaux ask questions about software. The engine runs configurable prompts across AI models, analyses brand citation rates against a configurable competitor peer set, generates prioritised recommendations, and produces channel-specific content to act on them.

---

## v1.4.0 — 2026-04-23

Azure App Service deployment support.

### Added

- **`startup.sh`** — App Service startup script. Creates `/home/data/results/` and `/home/data/config.json` on first run, installs Python dependencies, and starts uvicorn with a single worker (required for in-memory SSE queues).
- **`.github/workflows/deploy.yml`** — GitHub Actions workflow. Builds the React frontend then deploys the full package to Azure App Service on every push to `main`. Also triggerable manually via `workflow_dispatch`.
- **`DEPLOY.md`** — Step-by-step Azure deployment guide covering App Service creation, app settings, startup command, Easy Auth (Microsoft login for Bright staff), GitHub secrets, and troubleshooting.
- **`backend/main.py`** — Production static file serving. When `frontend/dist/` exists, FastAPI mounts Vite's hashed assets at `/assets` and serves `index.html` for all unmatched routes (SPA catch-all). Falls back to Vite dev server proxy in local development (dist not present).

### Changed

- **`backend/deps.py`** — `CONFIG_PATH` and `RESULTS_DIR` now read from `CONFIG_PATH` and `RESULTS_DIR` environment variables, falling back to the existing local paths. Allows Azure deployment to point both at `/home/data/` (persistent Azure Files storage) so config and run results survive new deployments.
- **`backend/requirements.txt`** — Added `aiofiles` (required by FastAPI's `StaticFiles` for async file serving).

### How to upgrade (Azure)

Set two new App Service environment variables before deploying:

| Variable | Value |
|---|---|
| `CONFIG_PATH` | `/home/data/config.json` |
| `RESULTS_DIR` | `/home/data/results` |

Set the App Service startup command to `bash /home/site/wwwroot/startup.sh`.

No `config.json` schema changes. Local development workflow is unchanged.

---

## v1.3.0 — 2026-04-17

Production readiness: repositories, services, controllers, and agent protocol.

The application layer has been fully restructured into a clean MVC architecture. `main.py` has been reduced from several hundred lines to 65 lines. Business logic, file I/O, and HTTP handling are now in separate, independently testable layers.

### Added

- **`backend/repositories/config_repository.py`** — `ConfigRepository` class owns all reads and writes to `config.json` and topic asset files. Exposes `load()`, `save()`, `ensure_peer_sets()`, `ensure_topic_assets()`, and `topic_to_key()`. Both ensure methods are idempotent and return `True` if the config was modified, so callers can decide whether to persist.
- **`backend/repositories/results_repository.py`** — `ResultsRepository` class owns all reads and writes to `backend/results/*.json`. Exposes `load(run_id)`, `save(run_id, data)`, `list_all()` (sorted by mtime ascending), and `find_content_item(content_id)` (scans all run files for a content item by ID).
- **`backend/services/config_service.py`** — `ConfigService` owns all 10 config operations: `get_config`, `add_prompt`, `update_prompt`, `delete_prompt`, `add_competitor`, `update_competitor`, `delete_competitor`, `add_peer_set`, `delete_peer_set`, `update_benchmark_brand`, and `update_models`. Holds an `asyncio.Lock` to serialise concurrent writes. Raises typed `AEOError` subclasses; never raises `HTTPException`.
- **`backend/services/run_service.py`** — `RunService` owns `list_runs()`, which assembles summary rows with human-readable `run_name` values and slimmed `by_topic` data (rates only, for the TrendChart). Duplicate (date, scope) pairs receive a `v1`/`v2` version suffix assigned by mtime.
- **`backend/services/content_service.py`** — `ContentService` owns channel normalisation (`_normalise_channel`), content generation, targeting generation, approval, and retrieval. Content and targeting are generated in parallel with `asyncio.gather`. The valid channel set of exactly 8 channels is enforced here.
- **`backend/deps.py`** — Application-level singletons for all repositories and services (`config_repo`, `results_repo`, `config_svc`, `run_svc`, `content_svc`). Single source of truth for paths (`CONFIG_PATH`, `RESULTS_DIR`, `ASSETS_DIR`). Controllers import from here.
- **`backend/controllers/config_controller.py`** — `APIRouter` with prefix `/config`. Each endpoint is 1–3 lines, delegating entirely to `config_svc`.
- **`backend/controllers/run_controller.py`** — `APIRouter` with prefix `/runs`. Handles `POST /runs` (trigger), `GET /runs` (list), `GET /runs/{run_id}` (detail), and `GET /runs/{run_id}/stream` (SSE). SSE state (`_run_queues`) lives in this module.
- **`backend/controllers/content_controller.py`** — `APIRouter` handling `/recommendations/{run_id}`, `POST /content`, `GET /content/{run_id}`, `PUT /content/{content_id}/approve`, and `GET /targeting/{run_id}`.
- **`backend/controllers/log_controller.py`** — `APIRouter` with prefix `/logs`. `GET /logs` accepts optional `level` and `limit` query parameters; `DELETE /logs` clears the buffer.
- **`backend/controllers/asset_controller.py`** — `APIRouter` with prefix `/assets`. `POST /assets/open` opens an asset file in the system default editor (macOS `open`), with path traversal protection.
- **`backend/agents/protocol.py`** — `QueryAgent` Protocol class documenting the never-raise contract. Every agent `query(job)` function must return a `QueryResult` with `status='success'` or `status='error'` and must never raise to the caller.
- **`backend/agents/registry.py`** — `AgentRegistration` dataclass and module-level `_REGISTRY` dict. `register(name, env_key, cost_per_token, module)` is called once per agent at module load time. `get_active(config, model_filter)` returns registrations for models that are registered, enabled in config, match the optional filter, and have a valid API key in the environment.

### Changed

- **`backend/main.py`** reduced to 65 lines. Now responsible only for: loading environment, validating required API keys, configuring logging, creating the FastAPI app with CORS middleware and the `AEOError` exception handler, and including the five routers.
- **Orchestrator** updated to use `registry.get_active()` instead of hardcoded model dicts, and `ResultsRepository` instead of inline file I/O.
- **Each query agent** (`query_claude.py`, `query_openai.py`, `query_gemini.py`, `query_perplexity.py`) self-registers with `registry.register()` at module load time. Adding a new AI model now requires only creating `query_<model>.py` and calling `register()` — no orchestrator changes needed.

### How to upgrade

No `config.json` changes required. The repository and service layer reads the same `config.json` and `results/*.json` format as v1.2.0. Restart the backend after updating.

---

## v1.2.0 — 2026-04-17

Production readiness: structured logging, typed exceptions, and Monitor UI.

### Added

- **`backend/core/logging.py`** — Structured logging module. `_LogBuffer` is a thread-safe ring buffer storing the last 500 log events in memory. `_BufferingHandler` writes structured dicts into the buffer on every log call. `_DevFormatter` produces coloured, human-readable output with run_id prefix and key=value context lines. `_JSONFormatter` produces one JSON object per line for log aggregators (Datadog, CloudWatch, etc.). `setup_logging()` configures the root `aeo` logger; `get_logger(__name__)` returns a child logger namespaced by module.
- **`backend/errors/exceptions.py`** — Typed `AEOError` exception hierarchy. `AEOError` is the base class carrying `message`, `context` dict, and `status_code`. Subclasses: `ConfigError` (400), `PromptNotFound` (404), `CompetitorNotFound` (404), `PeerSetNotFound` (404), `PeerSetAlreadyExists` (409), `RunError` (422), `RunNotFound` (404), `RecommendationsNotFound` (404), `NoActivePrompts` (422), `NoActiveModels` (422), `ContentError` (400), `ChannelNotSupported` (400), `ContentItemNotFound` (404), `AgentError` (500), `LLMParseError` (500), `MissingAPIKey` (500).
- **`@app.exception_handler(AEOError)`** in `main.py` — maps all typed errors to the correct HTTP status code and returns a JSON body with `detail` and `error_type` fields.
- **`GET /logs`** endpoint — returns recent log events from the in-memory buffer, newest first. Accepts optional `level` (DEBUG/INFO/WARNING/ERROR/CRITICAL) and `limit` (1–500, default 200) query parameters.
- **`DELETE /logs`** endpoint — clears the in-memory log buffer.
- **`frontend/src/tabs/Monitor.jsx`** — New Monitor tab. Shows four summary cards (Errors highlighted red if count > 0, Warnings, Info events, Debug events). Level filter buttons (ALL/ERROR/WARNING/INFO/DEBUG). Auto-refresh toggle (every 5 seconds) and manual refresh. Expandable log rows: main row shows level badge, time, source module, event message, and up to 2 context pills; expanded state shows all context key=value pairs. Clear buffer button with confirmation.
- **`frontend/src/App.jsx`** — Monitor tab wired into the navigation sidebar.
- Structured `INFO`/`DEBUG`/`WARNING` log events added to all agents (`query_claude`, `query_openai`, `query_gemini`, `query_perplexity`, `recommender`, `content_agent`, `targeting_agent`) and the orchestrator (run lifecycle: started, complete, aborted, recs failed).

### Changed

- All agents and services now raise typed `AEOError` subclasses instead of bare `Exception`.
- Orchestrator abort logic logs a `WARNING` when a model exceeds the 30% failure threshold and an `INFO` when the run completes or aborts.

### How to upgrade

No `config.json` changes required. Two new environment variables are available but optional:

| Variable | Values | Default |
|---|---|---|
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `LOG_FORMAT` | `dev`, `json` | `dev` |

Set `LOG_FORMAT=json` in `.env` for production/aggregator deployments.

---

## v1.1.0 — 2026-04-17

Configurable benchmark brand.

All hardcoded references to "Bright" as the measured brand have been replaced with a configurable `benchmark_brand` field read from `config.json`.

### Added

- **`PUT /config/benchmark_brand`** endpoint — accepts `{"name": "BrandName"}` and persists the new benchmark brand to `config.json`.
- **`BenchmarkBrandConfig` component** in `frontend/src/tabs/Configure.jsx` — shows the current benchmark brand with a Change button. If `brand_variants` keys are present in config, a dropdown is shown; otherwise a free-text input is used.

### Changed

- `config.json` gains a `"benchmark_brand": "Bright"` top-level field.
- Analysis output stores `benchmark_brand` in the run result file so that old results display correctly even after the benchmark brand is changed.
- All Insights components (`SummaryCards`, `TrendChart`, `CompetitorRankings`, `SentimentSnippets`, `LiveFeed`) accept a `benchmarkBrand` prop and use it in display labels and citation rate calculations.
- Backward compatible: run result files without `benchmark_brand` default to `"Bright"`.

### How to upgrade

Add `"benchmark_brand": "Bright"` to the top level of `backend/config.json`. If the field is absent, it will be written automatically on the next `PUT /config/benchmark_brand` call, but the frontend BenchmarkBrandConfig component will show an empty value until then.

```json
{
  "benchmark_brand": "Bright",
  "prompts": [...],
  ...
}
```

---

## v1.0.0 — 2026-04-17

Initial release.

### Added

- **Core AEO analysis engine** — runs a configurable set of prompts across Claude (claude-opus-4-6), GPT-4o, Gemini 1.5 Pro, and Perplexity (llama-3.1-sonar-large-128k-online). For each prompt/model combination, the response is parsed for brand citations from the configured peer set.
- **Citation rate analysis** — measures how often each brand in the peer set is cited in AI responses. Produces per-topic and per-model breakdowns, overall citation rates, and a watch-out list of topics/models where the benchmark brand citation rate is zero.
- **Competitor peer sets** — each topic has an independently configurable peer set of brands with variant name lists (e.g. "BrightPay", "Bright Pay", "brightpay.co.uk" all map to the same brand). Peer sets are auto-created when a new topic is added.
- **Recommendations engine** — after analysis, an AI-generated prioritised action list is produced by the recommender agent (Claude). Each recommendation carries priority, category, topic, finding, action, effort, impact, timeframe, and target channels.
- **Content generation** — channel-specific content is generated by `content_agent.py` (Claude only). Eight channels are supported: `linkedin`, `reddit`, `wikipedia`, `accountingweb`, `g2_outreach`, `trustpilot_outreach`, `pr_pitch`, `web_page`. Reddit content always requires human review before use.
- **Targeting agent** — generates customer profiles (role titles, company type, CRM query, outreach template, review ask) and PR placement recommendations (outlet, pitch angle, draft pitch) from each recommendation.
- **Run history** — every completed run is stored as a JSON file in `backend/results/` with the full result including analysis, recommendations, content items, and targeting results.
- **FastAPI backend** (`backend/main.py`) with async request handling and `uvicorn --reload` development server.
- **React 18 + Vite + Tailwind CSS frontend** with Bright brand colours, typography, and logo.
- **SSE live progress feed** — `GET /runs/{run_id}/stream` streams query progress events, phase transitions (querying → analysing → recommending), running cost, and the final summary to the browser in real time.
- **Configure tab** — manage prompts (add, edit, toggle active, delete), competitors and peer sets, model enable/disable toggles, and brand asset files. Topics are collapsed by default; each topic card shows the active prompt count and competitor count.
- **Run tab** — trigger runs with optional topic/model filters, watch the live feed, see the running API cost, and browse run history with human-readable run names.
- **Insights tab** — select a run from the dropdown; view summary cards (overall citation rate, total responses, failed calls, watch-outs), citation rate trend chart, competitor rankings per topic, sentiment snippets, recommendations list, and content queue.
- **Per-model abort threshold** — the orchestrator aborts only when all active models exceed a 30% failure rate. One model failing (e.g. OpenAI quota exhausted) does not abort a run where other models are healthy.
- **Topic asset files** — each topic automatically gets a corresponding `backend/assets/product-descriptions/{topic_key}.md` file used by the content agent. Legacy topics use pre-existing files (e.g. `brightpay-cloud.md` for the Payroll topic).
