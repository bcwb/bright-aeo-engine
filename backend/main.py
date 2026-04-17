"""
Bright AEO Engine — FastAPI backend.

Start with:
    cd bright-aeo-engine/backend
    uvicorn main:app --reload --port 8000
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ── API key validation on startup ──────────────────────────────────────────
_KEY_MAP = {
    "claude":     "ANTHROPIC_API_KEY",
    "openai":     "OPENAI_API_KEY",
    "gemini":     "GOOGLE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}
_REQUIRED_KEYS = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"]
_missing = [k for k in _REQUIRED_KEYS if not os.environ.get(k)]
if _missing:
    raise RuntimeError(
        f"\n\nMissing required API keys: {', '.join(_missing)}\n"
        f"Edit {ROOT / '.env'} and restart.\n"
    )
if not os.environ.get("PERPLEXITY_API_KEY"):
    print("INFO: PERPLEXITY_API_KEY not set — Perplexity queries will be skipped.")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agents import orchestrator
from agents.content_agent import generate_content, load_assets
from agents.targeting_agent import generate_targeting
from models import ContentJob, Recommendation, TargetingJob
from core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"
RESULTS_DIR = Path(__file__).parent / "results"
ASSETS_DIR  = Path(__file__).parent / "assets"
RESULTS_DIR.mkdir(exist_ok=True)

# ── Channel normalisation ──────────────────────────────────────────────────
_VALID_CHANNELS = {
    "linkedin", "reddit", "wikipedia", "accountingweb",
    "g2_outreach", "trustpilot_outreach", "pr_pitch", "web_page",
}

def _normalise_channel(ch: str) -> str | None:
    """Map a free-form channel name to a valid content_agent channel key.
    Returns None for channels that cannot be mapped."""
    c = ch.lower().strip()
    if c in _VALID_CHANNELS:
        return c
    if "linkedin" in c:
        return "linkedin"
    if "reddit" in c:
        return "reddit"
    if "wikipedia" in c or "wikidata" in c:
        return "wikipedia"
    if "accountingweb" in c or "accounting web" in c:
        return "accountingweb"
    if "trustpilot" in c:
        return "trustpilot_outreach"
    if "g2" in c and "capterra" not in c:
        return "g2_outreach"
    if ("pr" in c and any(x in c for x in ("pitch", "release", "press"))) or c == "pr":
        return "pr_pitch"
    if any(x in c for x in (
        "brightsg.com", "brightpay.co.uk", "brightsoftware",
        "web page", "webpage", "website", "faq", "blog",
        "landing page", "product page", "schema", "brightmanager",
        "brighttax", "brightaccounts",
    )):
        return "web_page"
    return None  # unrecognised — skip silently

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Bright AEO Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory state ────────────────────────────────────────────────────────
_config_lock = asyncio.Lock()
_run_queues: dict[str, asyncio.Queue] = {}   # run_id → SSE event queue


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _topic_to_key(topic: str) -> str:
    return topic.strip().lower().replace(" ", "_").replace("-", "_")


def _ensure_peer_sets(config: dict) -> bool:
    """Create an empty peer set for any topic that doesn't have one yet.
    Returns True if the config was modified."""
    changed = False
    for prompt in config.get("prompts", []):
        topic = prompt.get("topic", "").strip()
        if not topic:
            continue
        key = _topic_to_key(topic)
        if key not in config["peer_sets"]:
            config["peer_sets"][key] = []
            changed = True
    return changed


# For existing topics whose asset lives under a legacy filename, prefer that
# file rather than creating a new one.
_LEGACY_TOPIC_FILES: dict[str, str] = {
    "payroll":             "product-descriptions/brightpay-cloud.md",
    "practice_management": "product-descriptions/brightmanager.md",
    "tax_compliance":      "product-descriptions/brighttax.md",
    "cloud_accounting":    "product-descriptions/brightaccounts.md",
}

_TOPIC_ASSET_TEMPLATE = """\
# {topic} — Topic Brand Assets

> Auto-generated when topic '{topic}' was added.
> Populate this file with product and domain details before generating content.
> The content agent loads this file for every content generation request on this topic.

## What to include

- What this product / solution does (2–3 sentences, plain language)
- Key features relevant to UK/Ireland accountants and payroll bureaux
- Ideal customer profile for this topic area
- Specific proof points with numbers (only include verified figures)
- Awards and recognition relevant to this product
- How Bright differentiates from competitors in this space

## Content

[Populate this section — the more specific the detail, the better the generated content]
"""


def _ensure_topic_assets(config: dict) -> bool:
    """Create a topic asset .md file and config mapping for any topic without one.
    Returns True if the config was modified."""
    if "topic_assets" not in config:
        config["topic_assets"] = {}
    changed = False
    seen: set[str] = set()
    for prompt in config.get("prompts", []):
        topic = prompt.get("topic", "").strip()
        if not topic or topic in seen:
            continue
        seen.add(topic)
        key = _topic_to_key(topic)
        if key in config["topic_assets"]:
            continue
        # Prefer legacy filename if it exists, otherwise use key-based name
        filename = _LEGACY_TOPIC_FILES.get(key, f"product-descriptions/{key}.md")
        path = ASSETS_DIR / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(_TOPIC_ASSET_TEMPLATE.format(topic=topic), encoding="utf-8")
        config["topic_assets"][key] = filename
        changed = True
    return changed


def _load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _save_config(config: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def _load_run(run_id: str) -> dict:
    path = RESULTS_DIR / f"{run_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return json.loads(path.read_text())


def _save_run(run_id: str, data: dict) -> None:
    (RESULTS_DIR / f"{run_id}.json").write_text(json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------

@app.get("/config")
async def get_config():
    config = _load_config()
    changed = _ensure_peer_sets(config)
    changed |= _ensure_topic_assets(config)
    if changed:
        _save_config(config)
    return config


@app.post("/config/prompts", status_code=201)
async def add_prompt(prompt: dict):
    async with _config_lock:
        config = _load_config()
        if not prompt.get("id"):
            prompt["id"] = str(uuid.uuid4())[:8]
        prompt.setdefault("active", True)
        config["prompts"].append(prompt)
        _ensure_peer_sets(config)
        _ensure_topic_assets(config)   # auto-create asset file for new topic
        _save_config(config)
    logger.info("Config changed", extra={"context": {
        "change_type": "add_prompt", "entity_id": prompt["id"],
        "topic": prompt.get("topic"), "text": prompt.get("text", "")[:60],
    }})
    return prompt


@app.put("/config/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, updates: dict):
    async with _config_lock:
        config = _load_config()
        for p in config["prompts"]:
            if p["id"] == prompt_id:
                p.update(updates)
                _ensure_peer_sets(config)
                _ensure_topic_assets(config)   # auto-create asset file if topic changed
                _save_config(config)
                return p
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")


@app.delete("/config/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    async with _config_lock:
        config = _load_config()
        before = len(config["prompts"])
        config["prompts"] = [p for p in config["prompts"] if p["id"] != prompt_id]
        if len(config["prompts"]) == before:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_id}' not found")
        _save_config(config)
    logger.info("Config changed", extra={"context": {
        "change_type": "delete_prompt", "entity_id": prompt_id,
    }})
    return {"deleted": prompt_id}


@app.post("/config/competitors", status_code=201)
async def add_competitor(competitor: dict):
    peer_set = competitor.get("peer_set", "payroll")
    async with _config_lock:
        config = _load_config()
        if peer_set not in config["peer_sets"]:
            raise HTTPException(status_code=400, detail=f"Unknown peer_set '{peer_set}'")
        if not competitor.get("id"):
            competitor["id"] = str(uuid.uuid4())[:8]
        competitor.setdefault("variants", [competitor.get("name", "")])
        config["peer_sets"][peer_set].append(competitor)
        _save_config(config)
    return competitor


@app.put("/config/competitors/{competitor_id}")
async def update_competitor(competitor_id: str, updates: dict):
    async with _config_lock:
        config = _load_config()
        for peers in config["peer_sets"].values():
            for c in peers:
                if c["id"] == competitor_id:
                    for k, v in updates.items():
                        if k != "id":
                            c[k] = v
                    _save_config(config)
                    return c
        raise HTTPException(status_code=404, detail=f"Competitor '{competitor_id}' not found")


@app.post("/config/peer_sets", status_code=201)
async def add_peer_set(body: dict):
    label = body.get("label", "").strip()
    if not label:
        raise HTTPException(status_code=400, detail="label is required")
    key = label.lower().replace(" ", "_").replace("-", "_")
    async with _config_lock:
        config = _load_config()
        if key in config["peer_sets"]:
            raise HTTPException(status_code=409, detail=f"Peer set '{key}' already exists")
        config["peer_sets"][key] = []
        _save_config(config)
    return {"key": key, "label": label}


@app.delete("/config/peer_sets/{key}")
async def delete_peer_set(key: str):
    async with _config_lock:
        config = _load_config()
        if key not in config["peer_sets"]:
            raise HTTPException(status_code=404, detail=f"Peer set '{key}' not found")
        del config["peer_sets"][key]
        _save_config(config)
    return {"deleted": key}


@app.delete("/config/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str):
    async with _config_lock:
        config = _load_config()
        for set_name, peers in config["peer_sets"].items():
            before = len(peers)
            config["peer_sets"][set_name] = [c for c in peers if c["id"] != competitor_id]
            if len(config["peer_sets"][set_name]) < before:
                _save_config(config)
                logger.info("Config changed", extra={"context": {
                    "change_type": "delete_competitor", "entity_id": competitor_id,
                    "peer_set": set_name,
                }})
                return {"deleted": competitor_id}
        raise HTTPException(status_code=404, detail=f"Competitor '{competitor_id}' not found")


@app.put("/config/benchmark_brand")
async def update_benchmark_brand(body: dict):
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    async with _config_lock:
        config = _load_config()
        previous = config.get("benchmark_brand", "Bright")
        config["benchmark_brand"] = name
        _save_config(config)
    logger.info("Config changed", extra={"context": {
        "change_type": "update_benchmark_brand", "previous": previous, "new": name,
    }})
    return {"benchmark_brand": name}


@app.put("/config/models")
async def update_models(updates: dict):
    async with _config_lock:
        config = _load_config()
        for model_name, model_cfg in updates.items():
            if model_name in config["models"]:
                config["models"][model_name].update(model_cfg)
        _save_config(config)
    return _load_config()["models"]


# ---------------------------------------------------------------------------
# Assets endpoint
# ---------------------------------------------------------------------------

@app.post("/assets/open")
async def open_asset(body: dict):
    """Open a brand asset file in the system default editor (macOS: `open`)."""
    import subprocess
    filename = (body.get("file") or "").strip().lstrip("/")
    if not filename:
        raise HTTPException(status_code=400, detail="file is required")
    path = (ASSETS_DIR / filename).resolve()
    # Safety: ensure the resolved path stays inside ASSETS_DIR
    if not str(path).startswith(str(ASSETS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")
    subprocess.Popen(["open", str(path)])
    return {"opened": filename}


# ---------------------------------------------------------------------------
# Runs endpoints
# ---------------------------------------------------------------------------

@app.post("/runs", status_code=202)
async def trigger_run(body: dict = {}):
    run_id = str(uuid.uuid4())
    config = _load_config()
    topic_filter: str | None = body.get("topic")
    model_filter: str | None = body.get("model")

    queue: asyncio.Queue = asyncio.Queue()
    _run_queues[run_id] = queue

    async def _run_task():
        try:
            await orchestrator.run_analysis(
                run_id=run_id,
                config=config,
                topic_filter=topic_filter,
                model_filter=model_filter,
                progress_callback=queue.put,
            )
        except Exception as e:
            await queue.put({"type": "error", "run_id": run_id, "message": str(e)})

    asyncio.create_task(_run_task())
    logger.info("Run triggered", extra={"context": {
        "run_id": run_id,
        "topic_filter": topic_filter or "all",
        "model_filter": model_filter or "all",
    }})

    # Estimate call count for the UI cost preview
    active_prompts = [
        p for p in config["prompts"]
        if p.get("active", True) and (topic_filter is None or p["topic"] == topic_filter)
    ]
    active_models = [
        m for m, cfg in config["models"].items()
        if cfg.get("enabled", True) and (model_filter is None or m == model_filter)
    ]
    total_calls = len(active_prompts) * len(active_models)

    return {
        "run_id": run_id,
        "status": "running",
        "total_calls": total_calls,
        "stream_url": f"/runs/{run_id}/stream",
    }


@app.get("/runs")
async def list_runs():
    # Sort ascending by mtime so creation order is stable for version numbering
    paths = sorted(RESULTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    rows = []
    for path in paths:
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        analysis = data.get("analysis") or {}
        # Slim-down by_topic: keep rate per brand per topic for TrendChart
        by_topic_raw = analysis.get("by_topic") or {}
        by_topic = {
            topic: {
                brand: {"rate": bdata.get("rate", 0)}
                for brand, bdata in brands.items()
            }
            for topic, brands in by_topic_raw.items()
        }
        rows.append({
            "run_id":            data.get("run_id"),
            "run_date":          data.get("run_date"),
            "status":            data.get("status"),
            "topic_filter":      data.get("topic_filter"),
            "model_filter":      data.get("model_filter"),
            "total_prompts":     analysis.get("total_prompts", 0),
            "total_responses":   analysis.get("total_responses", 0),
            "failed_calls":      analysis.get("failed_calls", 0),
            "bright_overall_rate": analysis.get("bright_overall_rate"),
            "watchout_count":    len(analysis.get("watchouts", [])),
            "estimated_cost_usd": (data.get("meta") or {}).get("estimated_cost_usd"),
            "duration_seconds":  (data.get("meta") or {}).get("duration_seconds"),
            "by_topic":          by_topic,
        })

    # Count how many times each (date, scope) pair appears so we know
    # which groups need a version suffix
    from collections import Counter
    pair_counts: Counter = Counter(
        (r["run_date"], r["topic_filter"] or "All topics") for r in rows
    )
    pair_seen: Counter = Counter()

    for r in rows:
        scope = r["topic_filter"] or "All topics"
        key   = (r["run_date"], scope)
        pair_seen[key] += 1

        rate = (
            f"{round(r['bright_overall_rate'] * 100)}% cited"
            if r["bright_overall_rate"] is not None
            else r["status"]
        )

        if pair_counts[key] > 1:
            r["run_name"] = f"{r['run_date']} — {scope} v{pair_seen[key]} — {rate}"
        else:
            r["run_name"] = f"{r['run_date']} — {scope} — {rate}"

    # Return newest first
    rows.reverse()
    return rows


@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    return _load_run(run_id)


@app.get("/runs/{run_id}/stream")
async def stream_run(run_id: str):
    """SSE endpoint. Streams live progress events while the run is active."""

    # If run already finished, synthesise a complete event from saved file
    if run_id not in _run_queues:
        path = RESULTS_DIR / f"{run_id}.json"
        if path.exists():
            data = json.loads(path.read_text())
            analysis = data.get("analysis") or {}

            async def _completed():
                event = {
                    "type": "complete",
                    "run_id": run_id,
                    "status": data.get("status"),
                    "bright_overall_rate": analysis.get("bright_overall_rate"),
                    "total_responses": analysis.get("total_responses", 0),
                    "failed_calls": analysis.get("failed_calls", 0),
                }
                yield f"data: {json.dumps(event)}\n\n"

            return StreamingResponse(
                _completed(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found or not yet started")

    queue = _run_queues[run_id]

    async def _live_stream():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=25.0)
                except asyncio.TimeoutError:
                    # Keepalive ping so the connection doesn't drop
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
                    continue

                yield f"data: {json.dumps(event)}\n\n"

                if event.get("type") in ("complete", "error"):
                    _run_queues.pop(run_id, None)
                    break
        except asyncio.CancelledError:
            pass  # client disconnected

    return StreamingResponse(
        _live_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Recommendations endpoint
# ---------------------------------------------------------------------------

@app.get("/recommendations/{run_id}")
async def get_recommendations(run_id: str):
    data = _load_run(run_id)
    recs = data.get("recommendations")
    if not recs:
        error = data.get("recommendations_error")
        msg = f"No recommendations for run '{run_id}'"
        if error:
            msg += f". Generation failed: {error}"
        raise HTTPException(status_code=404, detail=msg)
    return recs


# ---------------------------------------------------------------------------
# Content pipeline endpoints
# ---------------------------------------------------------------------------

@app.post("/content", status_code=202)
async def trigger_content(body: dict):
    run_id = body.get("run_id")
    rec_priority = body.get("recommendation_priority")
    raw_channels: list[str] = body.get("channels", [])
    # Normalise to valid channel keys; deduplicate while preserving order
    seen: set[str] = set()
    channels: list[str] = []
    for ch in raw_channels:
        mapped = _normalise_channel(ch)
        if mapped and mapped not in seen:
            channels.append(mapped)
            seen.add(mapped)

    if not run_id or rec_priority is None or not channels:
        raise HTTPException(
            status_code=400,
            detail="Required: run_id, recommendation_priority, channels[]",
        )

    data = _load_run(run_id)
    recs_data = data.get("recommendations") or {}
    rec_list = recs_data.get("recommendations", [])
    rec_dict = next((r for r in rec_list if r["priority"] == rec_priority), None)
    if not rec_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation priority {rec_priority} not found in run '{run_id}'",
        )

    rec = Recommendation(**rec_dict)

    # Sentiment context from saved analysis
    analysis = data.get("analysis") or {}
    benchmark_brand = analysis.get("benchmark_brand") or "Bright"
    bright_snippets = (
        (analysis.get("brand_citations") or {})
        .get(benchmark_brand, {})
        .get("sentiment_snippets", [])
    )[:5]

    # Look up the topic-specific asset file from live config
    live_config = _load_config()
    topic_key = _topic_to_key(rec.topic)
    topic_asset_file = live_config.get("topic_assets", {}).get(topic_key)

    # Generate content for all requested channels in parallel
    content_jobs = [ContentJob(rec, ch, {}, bright_snippets, topic_asset_file) for ch in channels]
    content_results = await asyncio.gather(
        *[generate_content(j) for j in content_jobs],
        return_exceptions=True,
    )

    # Generate targeting (customer profile + PR placements) in parallel
    targeting_results = await asyncio.gather(
        generate_targeting(TargetingJob(rec, "customer_profile")),
        generate_targeting(TargetingJob(rec, "pr_placement")),
        return_exceptions=True,
    )

    # Build content items
    new_content_items: list[dict] = []
    for channel, result in zip(channels, content_results):
        if isinstance(result, Exception):
            item: dict = {
                "content_id": str(uuid.uuid4()),
                "run_id": run_id,
                "recommendation_priority": rec_priority,
                "channel": channel,
                "status": "error",
                "error": str(result),
                "content": "",
                "word_count": 0,
                "human_review_required": channel == "reddit",
                "reviewer_name": None,
                "reviewer_date": None,
            }
        else:
            item = {
                "content_id": str(uuid.uuid4()),
                "run_id": run_id,
                "recommendation_priority": rec_priority,
                "channel": result.channel,
                "content": result.content,
                "word_count": result.word_count,
                "human_review_required": result.human_review_required,
                "reviewer_name": None,
                "reviewer_date": None,
                "status": "draft",
            }
        new_content_items.append(item)

    # Build targeting items
    import dataclasses
    new_targeting: list[dict] = []
    for tr in targeting_results:
        if isinstance(tr, Exception):
            new_targeting.append({"error": str(tr), "recommendation_priority": rec_priority})
        else:
            new_targeting.append(dataclasses.asdict(tr))

    # Persist to run file
    data.setdefault("content_items", []).extend(new_content_items)
    data.setdefault("targeting_results", []).extend(new_targeting)
    _save_run(run_id, data)

    return {
        "generated_content": len(new_content_items),
        "content_items": new_content_items,
        "targeting": new_targeting,
    }


@app.get("/content/{run_id}")
async def get_content(run_id: str):
    data = _load_run(run_id)
    return data.get("content_items", [])


@app.put("/content/{content_id}/approve")
async def approve_content(content_id: str, body: dict):
    reviewer_name = (body.get("reviewer_name") or "").strip()
    if not reviewer_name:
        raise HTTPException(
            status_code=400,
            detail="reviewer_name is required to approve content",
        )

    for path in sorted(RESULTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        for item in data.get("content_items", []):
            if item.get("content_id") != content_id:
                continue
            # Reddit gate: reviewer_name must be present (already enforced above)
            item["reviewer_name"] = reviewer_name
            item["reviewer_date"] = date.today().isoformat()
            item["status"] = "approved"
            _save_run(data["run_id"], data)
            logger.info("Content approved", extra={"context": {
                "content_id": content_id, "reviewer": reviewer_name,
                "channel": item.get("channel"), "run_id": data["run_id"],
            }})
            return item

    raise HTTPException(status_code=404, detail=f"Content item '{content_id}' not found")


@app.get("/targeting/{run_id}")
async def get_targeting(run_id: str):
    data = _load_run(run_id)
    return data.get("targeting_results", [])
