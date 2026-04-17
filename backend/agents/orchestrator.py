"""
Orchestrator.

Coordinates a full AEO analysis run:
  1. Build job list from config (prompt × model combinations)
  2. Dispatch all jobs with per-model semaphores (max 3 concurrent)
  3. Emit SSE progress events via async callback after each job
  4. Abort if >30% of calls fail
  5. Run analysis agent on collected results
  6. Run recommendations agent on analysis output
  7. Save full results to results/{run_id}.json
  8. Emit "complete" event

progress_callback must be an async callable that accepts a dict.
"""

import asyncio
import dataclasses
import json
import os
import sys
import time
import uuid
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

from models import QueryJob, QueryResult
from agents import analyser, recommender
from agents import query_claude, query_openai, query_gemini, query_perplexity
from core.logging import get_logger

logger = get_logger(__name__)

RESULTS_DIR = Path(__file__).parent.parent / "results"
ABORT_THRESHOLD = 0.30          # abort if >30% of calls fail
MAX_CONCURRENT_PER_MODEL = 3
INTER_CALL_DELAY = 1.0          # seconds between calls to same model

_QUERY_AGENTS = {
    "claude":     query_claude,
    "openai":     query_openai,
    "gemini":     query_gemini,
    "perplexity": query_perplexity,
}

_COST_PER_TOKEN = {
    "claude":     0.000060,
    "openai":     0.000010,
    "gemini":     0.000004,
    "perplexity": 0.000001,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_full_brand_map(config: dict) -> dict[str, list[str]]:
    brand_map: dict[str, list[str]] = dict(config.get("brand_variants", {}))
    covered = {v.lower() for vs in brand_map.values() for v in vs}
    for peers in config.get("peer_sets", {}).values():
        for peer in peers:
            name = peer["name"]
            if name.lower() not in covered:
                brand_map[name] = peer.get("variants", [name])
                covered.update(v.lower() for v in brand_map[name])
    return brand_map


def _bright_mentioned(text: str, variants: list[str]) -> bool:
    t = text.lower()
    return any(v.lower() in t for v in variants)


def _top_n_brands(text: str, brand_map: dict[str, list[str]], n: int = 3) -> list[str]:
    """Return up to n canonical brand names found in text, ordered by first appearance."""
    text_lower = text.lower()
    hits: list[tuple[int, str]] = []
    for canonical, variants in brand_map.items():
        for v in variants:
            idx = text_lower.find(v.lower())
            if idx != -1:
                hits.append((idx, canonical))
                break
    hits.sort()
    seen: list[str] = []
    for _, brand in hits:
        if brand not in seen:
            seen.append(brand)
        if len(seen) >= n:
            break
    return seen


def _save_results(run_id: str, payload: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / f"{run_id}.json").write_text(
        json.dumps(payload, indent=2, default=str)
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run_analysis(
    run_id: str,
    config: dict,
    topic_filter: str | None,
    model_filter: str | None,
    progress_callback,
) -> None:
    """
    Full async analysis pipeline.

    progress_callback(event: dict) is awaited after every job and at lifecycle
    milestones (started / analysing / recommending / complete / error).
    """
    start_time = time.time()

    # ── 1. Build job list ──────────────────────────────────────────────────
    active_prompts = [
        p for p in config["prompts"]
        if p.get("active", True)
        and (topic_filter is None or p["topic"] == topic_filter)
    ]
    active_models = [
        m for m, cfg in config["models"].items()
        if cfg.get("enabled", True)
        and (model_filter is None or m == model_filter)
        and m in _QUERY_AGENTS
        and os.environ.get(f"{m.upper()}_API_KEY") or (
            m == "claude" and os.environ.get("ANTHROPIC_API_KEY")
        )
    ]

    # Filter out models whose key is definitely missing
    keyed_models = []
    key_map = {
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
    }
    for m in active_models:
        if os.environ.get(key_map.get(m, "")):
            keyed_models.append(m)
    active_models = keyed_models

    all_peer_names = [
        p["name"]
        for peers in config["peer_sets"].values()
        for p in peers
    ]
    brand_map = _build_full_brand_map(config)
    benchmark_brand = config.get("benchmark_brand", "Bright")
    bright_variants = config["brand_variants"].get(benchmark_brand, [])

    jobs: list[QueryJob] = [
        QueryJob(
            job_id=str(uuid.uuid4()),
            prompt=prompt["text"],
            topic=prompt["topic"],
            model=model,
            peer_set=all_peer_names,
        )
        for prompt in active_prompts
        for model in active_models
    ]
    total = len(jobs)

    logger.info("Run started", extra={"context": {
        "run_id": run_id, "total_jobs": total,
        "models": ",".join(active_models),
        "prompts": len(active_prompts),
        "topic_filter": topic_filter or "all",
        "model_filter": model_filter or "all",
    }})
    await progress_callback({
        "type": "started",
        "run_id": run_id,
        "total": total,
        "models": active_models,
        "message": f"Starting {total} queries ({len(active_prompts)} prompts × {len(active_models)} models)",
    })

    if total == 0:
        logger.warning("Run aborted — nothing to run", extra={"context": {
            "run_id": run_id, "active_prompts": len(active_prompts),
            "active_models": len(active_models),
        }})
        await progress_callback({
            "type": "error",
            "run_id": run_id,
            "message": "No active prompts or models to run. Check config.",
        })
        return

    # ── 2. Per-model semaphores + rate limiting ────────────────────────────
    semaphores = {m: asyncio.Semaphore(MAX_CONCURRENT_PER_MODEL) for m in active_models}
    last_call_time: dict[str, float] = {m: 0.0 for m in active_models}

    completed = 0
    failed = 0
    running_cost = 0.0
    aborted = False
    # Per-model counters so one broken model doesn't abort the whole run
    model_completed: dict[str, int] = {m: 0 for m in active_models}
    model_failed:    dict[str, int] = {m: 0 for m in active_models}
    query_results: list[QueryResult] = []

    async def run_job(job: QueryJob) -> QueryResult:
        nonlocal completed, failed, running_cost, aborted

        if aborted:
            return QueryResult(
                job_id=job.job_id, prompt=job.prompt, topic=job.topic,
                model=job.model, response_text="", status="error",
                error="Run aborted", tokens_used=0, latency_ms=0,
            )

        async with semaphores[job.model]:
            gap = INTER_CALL_DELAY - (time.time() - last_call_time[job.model])
            if gap > 0:
                await asyncio.sleep(gap)
            last_call_time[job.model] = time.time()
            result = await _QUERY_AGENTS[job.model].query(job)

        completed += 1
        model_completed[job.model] += 1
        if result.status == "error":
            failed += 1
            model_failed[job.model] += 1
        else:
            running_cost += result.tokens_used * _COST_PER_TOKEN.get(job.model, 0)

        # Abort only if ALL models are failing above the threshold — one bad
        # model (e.g. quota exceeded on OpenAI) should not kill a healthy run.
        models_over_threshold = [
            m for m in active_models
            if model_completed[m] >= 2  # need at least 2 results to judge
            and model_failed[m] / model_completed[m] > ABORT_THRESHOLD
        ]
        if len(models_over_threshold) == len(active_models):
            logger.warning("Run aborted — all models exceeding failure threshold", extra={"context": {
                "run_id": run_id, "failed": failed, "completed": completed,
                "threshold_pct": int(ABORT_THRESHOLD * 100),
                "models_over_threshold": ",".join(models_over_threshold),
            }})
            aborted = True

        await progress_callback({
            "type": "progress",
            "job_id": result.job_id,
            "model": result.model,
            "prompt": result.prompt[:80],
            "topic": result.topic,
            "status": result.status,
            "error": result.error,
            "bright_mentioned": _bright_mentioned(result.response_text, bright_variants),
            "top_brands": _top_n_brands(result.response_text, brand_map),
            "latency_ms": result.latency_ms,
            "tokens_used": result.tokens_used,
            "completed": completed,
            "total": total,
            "running_cost_usd": round(running_cost, 4),
        })

        return result

    # ── 3. Dispatch all jobs ───────────────────────────────────────────────
    query_results = list(await asyncio.gather(*[run_job(j) for j in jobs]))

    if aborted:
        payload = {
            "run_id": run_id,
            "run_date": date.today().isoformat(),
            "status": "aborted",
            "topic_filter": topic_filter,
            "model_filter": model_filter,
            "config_snapshot": config,
            "query_results": [dataclasses.asdict(r) for r in query_results],
            "analysis": None,
            "recommendations": None,
            "content_items": [],
            "targeting_results": [],
            "meta": {
                "total_tokens": sum(r.tokens_used for r in query_results),
                "estimated_cost_usd": round(running_cost, 4),
                "duration_seconds": round(time.time() - start_time, 1),
                "failed_calls": failed,
            },
        }
        _save_results(run_id, payload)
        await progress_callback({
            "type": "error",
            "run_id": run_id,
            "message": (
                f"Run aborted: {failed}/{completed} calls failed "
                f"(>{int(ABORT_THRESHOLD * 100)}% threshold). "
                f"Partial results saved."
            ),
        })
        return

    # ── 4. Analysis ────────────────────────────────────────────────────────
    await progress_callback({
        "type": "analysing",
        "run_id": run_id,
        "message": f"Analysing {len(query_results)} responses...",
    })
    analysis = analyser.analyse(query_results, config)
    logger.info("Analysis complete", extra={"context": {
        "run_id": run_id,
        "total_responses": analysis.total_responses,
        "failed_calls": analysis.failed_calls,
        "benchmark_brand": analysis.benchmark_brand,
        "benchmark_rate_pct": round(analysis.bright_overall_rate * 100),
        "watchouts": len(analysis.watchouts),
    }})

    # ── 5. Recommendations ─────────────────────────────────────────────────
    await progress_callback({
        "type": "recommending",
        "run_id": run_id,
        "message": "Generating AEO recommendations...",
    })
    recs = None
    recs_error = None
    try:
        recs = await recommender.generate_recommendations(analysis, run_id, topic_filter)
        logger.info("Recommendations generated", extra={"context": {
            "run_id": run_id,
            "recommendation_count": len(recs.recommendations),
        }})
    except Exception as e:
        recs_error = str(e)
        logger.error("Recommendations failed", extra={"context": {
            "run_id": run_id, "error": recs_error[:200],
        }})
        await progress_callback({
            "type": "warning",
            "run_id": run_id,
            "message": f"Recommendations failed: {recs_error}. Analysis saved — retry via UI.",
        })

    # ── 6. Save results ────────────────────────────────────────────────────
    payload = {
        "run_id": run_id,
        "run_date": date.today().isoformat(),
        "status": "complete",
        "topic_filter": topic_filter,
        "model_filter": model_filter,
        "config_snapshot": config,
        "query_results": [dataclasses.asdict(r) for r in query_results],
        "analysis": dataclasses.asdict(analysis),
        "recommendations": dataclasses.asdict(recs) if recs else None,
        "recommendations_error": recs_error,
        "content_items": [],
        "targeting_results": [],
        "meta": {
            "total_tokens": sum(r.tokens_used for r in query_results),
            "estimated_cost_usd": round(running_cost, 4),
            "duration_seconds": round(time.time() - start_time, 1),
            "failed_calls": failed,
        },
    }
    _save_results(run_id, payload)

    # ── 7. Complete event ──────────────────────────────────────────────────
    logger.info("Run complete", extra={"context": {
        "run_id": run_id,
        "status": "complete",
        "duration_s": round(time.time() - start_time, 1),
        "total_responses": analysis.total_responses,
        "failed_calls": analysis.failed_calls,
        "benchmark_rate_pct": round(analysis.bright_overall_rate * 100),
        "cost_usd": round(running_cost, 4),
    }})
    await progress_callback({
        "type": "complete",
        "run_id": run_id,
        "benchmark_brand": analysis.benchmark_brand,
        "bright_overall_rate": analysis.bright_overall_rate,
        "total_responses": analysis.total_responses,
        "failed_calls": analysis.failed_calls,
        "watchouts": analysis.watchouts,
        "recommendation_count": len(recs.recommendations) if recs else 0,
        "estimated_cost_usd": round(running_cost, 4),
        "duration_seconds": round(time.time() - start_time, 1),
    })
