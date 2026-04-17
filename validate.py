"""
Pre-flight validation. Run before main.py on first setup.
Tests all four query agents with a single prompt.
Prints raw responses and extracted brand mentions.
Estimates cost of a full run.

Usage:
    cd bright-aeo-engine
    python validate.py
"""

import asyncio
import json
import os
import re
import sys
import uuid

# Make backend importable from project root
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

# ---------------------------------------------------------------------------
# Test fixtures (from brief)
# ---------------------------------------------------------------------------

TEST_PROMPT = "best payroll software for uk accountancy bureaux 2026"

TEST_PEER_SET = [
    "BrightPay", "Moneysoft", "Sage Payroll", "Staffology",
    "Xero Payroll", "Employment Hero", "FreshPay", "Qtac",
]

BRIGHT_VARIANTS = [
    "Bright", "BrightPay", "Bright Pay", "brightpay.co.uk", "brightsg.com",
    "BrightManager", "BrightTax", "BrightAccountsProduction",
]

# Rough blended cost per token for planning estimates.
# Verify against current API pricing before budgeting.
COST_PER_TOKEN = {
    "claude":     0.000060,   # ~$60/M  (Opus-class)
    "openai":     0.000010,   # ~$10/M
    "gemini":     0.000004,   # ~$4/M
    "perplexity": 0.000001,   # ~$1/M
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_env() -> list[str]:
    required = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "PERPLEXITY_API_KEY"]
    return [k for k in required if not os.environ.get(k)]


def build_brand_map() -> dict[str, list[str]]:
    """Map canonical brand → variants to search for."""
    brand_map: dict[str, list[str]] = {"Bright": BRIGHT_VARIANTS}
    for brand in TEST_PEER_SET:
        if brand != "BrightPay":  # BrightPay is covered under Bright
            brand_map[brand] = [brand]
    return brand_map


def find_brand_positions(text: str) -> dict[str, int]:
    """Return {canonical_brand: ordinal_position} sorted by first appearance."""
    text_lower = text.lower()
    char_positions: dict[str, int] = {}

    for canonical, variants in build_brand_map().items():
        first_pos = None
        for v in variants:
            idx = text_lower.find(v.lower())
            if idx != -1 and (first_pos is None or idx < first_pos):
                first_pos = idx
        if first_pos is not None:
            char_positions[canonical] = first_pos

    sorted_brands = sorted(char_positions.items(), key=lambda x: x[1])
    return {brand: rank + 1 for rank, (brand, _) in enumerate(sorted_brands)}


def find_sentiment_snippet(text: str) -> str | None:
    """Return the first sentence containing any Bright variant."""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if any(v.lower() in sentence.lower() for v in BRIGHT_VARIANTS):
            snippet = sentence.strip()
            return snippet[:220] + "..." if len(snippet) > 220 else snippet
    return None


def bright_mentioned(text: str) -> bool:
    return any(v.lower() in text.lower() for v in BRIGHT_VARIANTS)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_result(label: str, result) -> None:
    print(f"\n{'─' * 62}")
    print(f"  MODEL      : {label.upper()}")
    print(f"  STATUS     : {result.status}")

    if result.status == "error":
        print(f"  ERROR      : {result.error}")
        return

    mentioned = bright_mentioned(result.response_text)
    positions = find_brand_positions(result.response_text)
    snippet   = find_sentiment_snippet(result.response_text)

    print(f"  LATENCY    : {result.latency_ms}ms")
    print(f"  TOKENS     : {result.tokens_used}")
    print(f"  RESP LEN   : {len(result.response_text)} chars")
    print(f"  BRIGHT     : {'✓ MENTIONED' if mentioned else '✗ NOT MENTIONED'}")

    if positions:
        pos_str = "  ".join(f"{b}=#{p}" for b, p in sorted(positions.items(), key=lambda x: x[1]))
        print(f"  POSITIONS  : {pos_str}")

    if snippet:
        print(f"  SNIPPET    : \"{snippet}\"")

    preview = result.response_text[:300].replace("\n", " ")
    print(f"\n  PREVIEW    : {preview}...")


def print_cost_estimate(results: list, prompt_count: int, model_count: int) -> None:
    successful = [r for r in results if r.status == "success"]
    if not successful:
        print("\n  Cannot estimate cost — no successful responses.")
        return

    avg_tokens = sum(r.tokens_used for r in successful) / len(successful)
    total_calls = prompt_count * model_count
    estimated_cost = sum(
        avg_tokens * COST_PER_TOKEN.get(r.model, 0.000010) * prompt_count
        for r in successful
    )

    print(f"\n{'=' * 62}")
    print(f"  FULL RUN ESTIMATE  (based on test response sizes)")
    print(f"{'=' * 62}")
    print(f"  Active prompts  : {prompt_count}")
    print(f"  Active models   : {model_count}")
    print(f"  Total API calls : {total_calls}")
    print(f"  Avg tokens/call : {int(avg_tokens)}")
    print(f"  Est. total cost : ~${estimated_cost:.2f} USD")
    print(f"  (Rates are approximate — verify current API pricing)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    print("=" * 62)
    print("  BRIGHT AEO ENGINE — PRE-FLIGHT VALIDATION")
    print("=" * 62)

    # 1. Check env vars
    missing = check_env()
    if missing:
        print(f"\n  MISSING API KEYS: {', '.join(missing)}")
        print(f"  Copy .env.example to .env and fill in all four keys.")
        print(f"  Exiting.\n")
        sys.exit(1)
    print("\n  API keys : all four present ✓")

    # 2. Load config for prompt/model counts
    config_path = os.path.join(ROOT, "backend", "config.json")
    with open(config_path) as f:
        config = json.load(f)
    active_prompts = [p for p in config["prompts"] if p["active"]]
    active_models  = [k for k, v in config["models"].items() if v["enabled"]]

    # 3. Import agents
    from agents import query_claude, query_openai, query_gemini, query_perplexity
    from models import QueryJob

    def make_job(model: str) -> QueryJob:
        return QueryJob(
            job_id=str(uuid.uuid4()),
            prompt=TEST_PROMPT,
            topic="Payroll",
            model=model,
            peer_set=TEST_PEER_SET,
        )

    print(f"  Prompt   : \"{TEST_PROMPT}\"")
    print(f"  Running all 4 models in parallel...\n")

    # 4. Run all four in parallel
    results = await asyncio.gather(
        query_claude.query(make_job("claude")),
        query_openai.query(make_job("openai")),
        query_gemini.query(make_job("gemini")),
        query_perplexity.query(make_job("perplexity")),
    )

    for label, result in zip(["claude", "openai", "gemini", "perplexity"], results):
        print_result(label, result)

    # 5. Cost estimate
    print_cost_estimate(list(results), len(active_prompts), len(active_models))

    # 6. Google AI Overview note (cannot be automated)
    print(f"\n  NOTE: Google AI Overview cannot be queried programmatically.")
    print(f"  Manual check: search each prompt in Google and note whether")
    print(f"  Bright appears in the AI Overview box. Log results manually.")

    # 7. GO / NO-GO
    all_ok = all(r.status == "success" for r in results)
    failed = [r.model for r in results if r.status == "error"]
    print(f"\n{'=' * 62}")
    if all_ok:
        print(f"  GO ✓  All 4 models responding. Ready to run main.py.")
    else:
        print(f"  NO-GO ✗  Failed models: {', '.join(failed)}")
        print(f"  Fix the errors above before proceeding.")
    print(f"{'=' * 62}\n")


if __name__ == "__main__":
    asyncio.run(main())
