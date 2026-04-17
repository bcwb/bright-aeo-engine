"""
ContentService — orchestrates content generation, approval, and retrieval.

Owns channel normalisation. Raises typed AEOErrors; never raises HTTPException.

Usage:
    from services.content_service import ContentService

    svc = ContentService(config_repo, results_repo)
    result = await svc.trigger_content({"run_id": ..., "recommendation_priority": 1, "channels": [...]})
    item   = await svc.approve_content(content_id, reviewer_name)
"""

import asyncio
import dataclasses
import uuid
from datetime import date

from agents.content_agent import generate_content
from agents.targeting_agent import generate_targeting
from core.logging import get_logger
from errors.exceptions import ContentError, ContentItemNotFound
from models import ContentJob, Recommendation, TargetingJob
from repositories.config_repository import ConfigRepository
from repositories.results_repository import ResultsRepository

logger = get_logger(__name__)

_VALID_CHANNELS = {
    "linkedin", "reddit", "wikipedia", "accountingweb",
    "g2_outreach", "trustpilot_outreach", "pr_pitch", "web_page",
}


def _normalise_channel(ch: str) -> str | None:
    """Map a free-form channel name to a valid content_agent channel key.
    Returns None for channels that cannot be mapped — caller skips them silently."""
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
    return None


class ContentService:
    def __init__(self, config_repo: ConfigRepository, results_repo: ResultsRepository) -> None:
        self._config_repo  = config_repo
        self._results_repo = results_repo

    async def trigger_content(self, body: dict) -> dict:
        run_id       = body.get("run_id")
        rec_priority = body.get("recommendation_priority")
        raw_channels: list[str] = body.get("channels", [])

        # Normalise channel names; deduplicate while preserving order
        seen: set[str] = set()
        channels: list[str] = []
        for ch in raw_channels:
            mapped = _normalise_channel(ch)
            if mapped and mapped not in seen:
                channels.append(mapped)
                seen.add(mapped)

        if not run_id or rec_priority is None or not channels:
            raise ContentError("Required: run_id, recommendation_priority, channels[]")

        data = self._results_repo.load(run_id)
        recs_data = data.get("recommendations") or {}
        rec_dict  = next(
            (r for r in recs_data.get("recommendations", []) if r["priority"] == rec_priority),
            None,
        )
        if not rec_dict:
            raise ContentError(
                f"Recommendation priority {rec_priority} not found in run '{run_id}'",
                context={"run_id": run_id, "priority": rec_priority},
            )

        rec = Recommendation(**rec_dict)

        # Sentiment context from saved analysis
        analysis        = data.get("analysis") or {}
        benchmark_brand = analysis.get("benchmark_brand") or "Bright"
        bright_snippets = (
            (analysis.get("brand_citations") or {})
            .get(benchmark_brand, {})
            .get("sentiment_snippets", [])
        )[:5]

        # Topic-specific asset file from live config
        live_config     = self._config_repo.load()
        topic_key       = self._config_repo.topic_to_key(rec.topic)
        topic_asset_file = live_config.get("topic_assets", {}).get(topic_key)

        # Generate content and targeting in parallel
        content_jobs = [ContentJob(rec, ch, {}, bright_snippets, topic_asset_file) for ch in channels]
        content_results, targeting_results = await asyncio.gather(
            asyncio.gather(*[generate_content(j) for j in content_jobs], return_exceptions=True),
            asyncio.gather(
                generate_targeting(TargetingJob(rec, "customer_profile")),
                generate_targeting(TargetingJob(rec, "pr_placement")),
                return_exceptions=True,
            ),
        )

        # Build content item dicts
        new_content_items: list[dict] = []
        for channel, result in zip(channels, content_results):
            if isinstance(result, Exception):
                item: dict = {
                    "content_id": str(uuid.uuid4()),
                    "run_id":     run_id,
                    "recommendation_priority": rec_priority,
                    "channel":    channel,
                    "status":     "error",
                    "error":      str(result),
                    "content":    "",
                    "word_count": 0,
                    "human_review_required": channel == "reddit",
                    "reviewer_name": None,
                    "reviewer_date": None,
                }
            else:
                item = {
                    "content_id": str(uuid.uuid4()),
                    "run_id":     run_id,
                    "recommendation_priority": rec_priority,
                    "channel":    result.channel,
                    "content":    result.content,
                    "word_count": result.word_count,
                    "human_review_required": result.human_review_required,
                    "reviewer_name": None,
                    "reviewer_date": None,
                    "status":     "draft",
                }
            new_content_items.append(item)

        # Build targeting dicts
        new_targeting: list[dict] = []
        for tr in targeting_results:
            if isinstance(tr, Exception):
                new_targeting.append({"error": str(tr), "recommendation_priority": rec_priority})
            else:
                new_targeting.append(dataclasses.asdict(tr))

        # Persist
        data.setdefault("content_items", []).extend(new_content_items)
        data.setdefault("targeting_results", []).extend(new_targeting)
        self._results_repo.save(run_id, data)

        return {
            "generated_content": len(new_content_items),
            "content_items":     new_content_items,
            "targeting":         new_targeting,
        }

    async def approve_content(self, content_id: str, reviewer_name: str) -> dict:
        if not reviewer_name:
            raise ContentError("reviewer_name is required to approve content")

        found = self._results_repo.find_content_item(content_id)
        if found is None:
            raise ContentItemNotFound(
                f"Content item '{content_id}' not found",
                context={"content_id": content_id},
            )

        data, item = found
        item["reviewer_name"] = reviewer_name
        item["reviewer_date"] = date.today().isoformat()
        item["status"]        = "approved"
        self._results_repo.save(data["run_id"], data)
        logger.info("Content approved", extra={"context": {
            "content_id": content_id,
            "reviewer":   reviewer_name,
            "channel":    item.get("channel"),
            "run_id":     data["run_id"],
        }})
        return item

    def get_content(self, run_id: str) -> list:
        return self._results_repo.load(run_id).get("content_items", [])

    def get_targeting(self, run_id: str) -> list:
        return self._results_repo.load(run_id).get("targeting_results", [])
