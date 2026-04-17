"""
Analysis agent.

Accepts a list of QueryResult objects and a config dict.
Returns a fully populated AnalysisOutput with:
  - Per-brand citation counts, rates, ordinal positions, and sentiment snippets
  - Breakdowns by topic and by model
  - Bright overall citation rate
  - Watch-outs (topic or model where Bright = 0%)
  - Estimated API cost
"""

import os
import re
import sys
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from models import AnalysisOutput, BrandCitation, QueryResult

# Rough blended cost per token for estimation only — verify against current API pricing.
_COST_PER_TOKEN: dict[str, float] = {
    "claude":     0.000060,
    "openai":     0.000010,
    "gemini":     0.000004,
    "perplexity": 0.000001,
}


# ---------------------------------------------------------------------------
# Brand map builder
# ---------------------------------------------------------------------------

def _build_brand_map(config: dict) -> dict[str, list[str]]:
    """
    Build {canonical_brand: [variants]} from config.

    Priority order:
      1. brand_variants — consolidated brands (e.g. Bright with all product name variants)
      2. peer_sets — individual competitors, skipped if already covered under a canonical brand
    """
    brand_map: dict[str, list[str]] = dict(config.get("brand_variants", {}))

    # Track every variant string already mapped to avoid double-counting
    covered: set[str] = {
        v.lower()
        for variants in brand_map.values()
        for v in variants
    }

    for peers in config.get("peer_sets", {}).values():
        for peer in peers:
            name: str = peer["name"]
            variants: list[str] = peer.get("variants", [name])
            # Skip if the canonical name itself is already a known variant
            # (e.g. "BrightPay" is listed under Bright's variants)
            if name.lower() in covered:
                continue
            if name not in brand_map:
                brand_map[name] = variants
                covered.update(v.lower() for v in variants)

    return brand_map


# ---------------------------------------------------------------------------
# Per-response extraction
# ---------------------------------------------------------------------------

def _find_sentence(text: str, variant: str) -> str | None:
    """Return the first sentence that contains variant (case-insensitive)."""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if variant.lower() in sentence.lower():
            return sentence.strip()
    return None


def _extract_mentions(
    text: str, brand_map: dict[str, list[str]]
) -> dict[str, dict]:
    """
    Scan a single response for brand mentions.

    Returns {canonical_brand: {position: int, snippet: str|None}}
    where position is the ordinal rank by first character appearance (1 = first mentioned).
    Each canonical brand is counted at most once regardless of how many variants appear.
    """
    text_lower = text.lower()

    # Find earliest character position for each canonical brand
    char_positions: dict[str, tuple[int, str]] = {}
    for canonical, variants in brand_map.items():
        first_pos: int | None = None
        first_variant: str | None = None
        for v in variants:
            idx = text_lower.find(v.lower())
            if idx != -1 and (first_pos is None or idx < first_pos):
                first_pos = idx
                first_variant = v
        if first_pos is not None:
            char_positions[canonical] = (first_pos, first_variant)

    # Convert character positions to ordinal ranks
    sorted_brands = sorted(char_positions.items(), key=lambda x: x[1][0])
    mentions: dict[str, dict] = {}
    for ordinal, (canonical, (_, variant)) in enumerate(sorted_brands, 1):
        mentions[canonical] = {
            "position": ordinal,
            "snippet": _find_sentence(text, variant),
        }
    return mentions


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _build_citations(
    mentions_list: list[dict], total_responses: int
) -> dict[str, BrandCitation]:
    """Aggregate per-response mention dicts into BrandCitation objects."""
    if total_responses == 0:
        return {}

    agg: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "positions": [], "snippets": []}
    )

    for mentions in mentions_list:
        for canonical, data in mentions.items():
            agg[canonical]["count"] += 1
            agg[canonical]["positions"].append(data["position"])
            if data["snippet"]:
                agg[canonical]["snippets"].append(data["snippet"])

    return {
        canonical: BrandCitation(
            brand=canonical,
            count=d["count"],
            rate=round(d["count"] / total_responses, 4),
            positions=d["positions"],
            sentiment_snippets=d["snippets"],
        )
        for canonical, d in agg.items()
    }


def _estimate_cost(results: list[QueryResult]) -> float:
    return round(
        sum(
            r.tokens_used * _COST_PER_TOKEN.get(r.model, 0.000010)
            for r in results
        ),
        4,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyse(results: list[QueryResult], config: dict) -> AnalysisOutput:
    """
    Main entry point.  Accepts raw QueryResult list + loaded config dict.
    Returns fully populated AnalysisOutput.
    """
    brand_map = _build_brand_map(config)
    benchmark_brand = config.get("benchmark_brand", "Bright")
    successful = [r for r in results if r.status == "success"]
    failed_calls = len(results) - len(successful)
    total_responses = len(successful)

    # Extract mentions for every successful response
    all_mentions = [
        _extract_mentions(r.response_text, brand_map) for r in successful
    ]

    # Overall brand citations
    brand_citations = _build_citations(all_mentions, total_responses)

    # Break down by topic
    topics = sorted({r.topic for r in successful})
    by_topic: dict[str, dict[str, BrandCitation]] = {}
    for topic in topics:
        topic_results = [r for r in successful if r.topic == topic]
        topic_mentions = [
            _extract_mentions(r.response_text, brand_map) for r in topic_results
        ]
        by_topic[topic] = _build_citations(topic_mentions, len(topic_results))

    # Break down by model
    models = sorted({r.model for r in successful})
    by_model: dict[str, dict[str, BrandCitation]] = {}
    for model in models:
        model_results = [r for r in successful if r.model == model]
        model_mentions = [
            _extract_mentions(r.response_text, brand_map) for r in model_results
        ]
        by_model[model] = _build_citations(model_mentions, len(model_results))

    # Benchmark brand overall rate
    _zero_cite = BrandCitation(benchmark_brand, 0, 0.0, [], [])
    bright_overall_rate = brand_citations.get(benchmark_brand, _zero_cite).rate

    # Watch-outs: any topic or model where benchmark brand citation rate = 0%
    watchouts: list[str] = [
        f"Topic '{topic}': {benchmark_brand} not cited in any response"
        for topic, citations in by_topic.items()
        if citations.get(benchmark_brand, _zero_cite).rate == 0.0
    ] + [
        f"Model '{model}': {benchmark_brand} not cited in any response"
        for model, citations in by_model.items()
        if citations.get(benchmark_brand, _zero_cite).rate == 0.0
    ]

    return AnalysisOutput(
        run_date=date.today().isoformat(),
        total_prompts=len({(r.prompt, r.topic) for r in results}),
        total_responses=total_responses,
        failed_calls=failed_calls,
        brand_citations=brand_citations,
        by_topic=by_topic,
        by_model=by_model,
        benchmark_brand=benchmark_brand,
        bright_overall_rate=bright_overall_rate,
        watchouts=watchouts,
        estimated_cost_usd=_estimate_cost(successful),
    )
