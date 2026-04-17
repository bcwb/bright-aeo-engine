"""
Targeting agent.

Two modes:

  customer_profile
    Builds an ideal customer profile for review / testimonial outreach.
    Output: CustomerProfile with CRM query, outreach email template, and review ask.

  pr_placement
    Scores priority media outlets and generates a tailored pitch per outlet.
    Output: list[PRPlacement] ranked by citation_frequency then audience_fit.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from models import CustomerProfile, PRPlacement, TargetingJob, TargetingResult

_MODEL = "claude-opus-4-6"

# Priority outlets from the brief — citation_frequency is 0 until real analysis data
# is passed in from the orchestrator. Ordering updated at runtime.
_PR_OUTLETS = [
    "AccountingWEB",
    "TechRadar",
    "startups.co.uk",
    "smallbusiness.co.uk",
    "Reddit r/UKAccountants",
    "Reddit r/payroll",
]

_CUSTOMER_PROFILE_SYSTEM = """\
You are a customer success strategist for Bright Software Group —
a UK/Ireland accounting and payroll software company whose customers are
accountants, payroll bureaux, and accountancy practices.

Your task: generate a detailed ideal customer profile for testimonial and
review outreach, targeting the specific content gap identified in the AEO
recommendation. The profile should identify the exact type of existing Bright
customer most likely to leave a credible, specific review that addresses the gap.

Bright products: BrightPay Cloud (payroll), BrightManager (practice management),
BrightTax (tax compliance), BrightAccountsProduction (accounts production).
Bright's ICP: UK/Ireland accountancy bureaux and practices — NOT direct SMEs.

Return ONLY valid JSON. No preamble. No markdown fences.
Schema:
{
  "product": string,
  "role_titles": [string],
  "company_type": string,
  "company_size_range": string,
  "migration_window": string,
  "crm_query": string,
  "outreach_template": string,
  "review_ask": string,
  "expected_pool_size": string,
  "expected_yield": string
}\
"""

_PR_PLACEMENT_SYSTEM = """\
You are a PR strategist for Bright Software Group —
a UK/Ireland accounting and payroll software company whose audience is
accountants, payroll bureaux, and accountancy practices.

Your task: for each media outlet listed, generate a tailored PR pitch that
addresses the specific AEO content gap in the recommendation. Each pitch must
be specific to the outlet's editorial focus and audience, not a generic press release.

Return ONLY valid JSON. No preamble. No markdown fences.
Schema:
{
  "placements": [
    {
      "outlet": string,
      "citation_frequency": integer,
      "audience_fit": "High" | "Medium" | "Low",
      "lead_time": string,
      "pitch_angle": string,
      "draft_pitch": string,
      "contact_approach": string
    }
  ]
}\
"""


def _strip_fences(raw: str) -> str:
    """Remove accidental markdown code fences from a JSON response."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def generate_targeting(job: TargetingJob) -> TargetingResult:
    """
    Generate targeting output for a recommendation.
    mode="customer_profile" → CustomerProfile
    mode="pr_placement"     → list[PRPlacement] ranked by impact
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    rec = job.recommendation

    # ------------------------------------------------------------------
    if job.mode == "customer_profile":
        user_msg = (
            f"Generate an ideal customer profile for review outreach based on "
            f"this AEO recommendation:\n\n"
            f"Priority : {rec.priority}\n"
            f"Category : {rec.category}\n"
            f"Topic    : {rec.topic}\n"
            f"Finding  : {rec.finding}\n"
            f"Action   : {rec.action}"
        )
        message = await client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            system=_CUSTOMER_PROFILE_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        data = json.loads(_strip_fences(message.content[0].text))

        profile = CustomerProfile(
            product=data["product"],
            role_titles=data["role_titles"],
            company_type=data["company_type"],
            company_size_range=data["company_size_range"],
            migration_window=data["migration_window"],
            crm_query=data["crm_query"],
            outreach_template=data["outreach_template"],
            review_ask=data["review_ask"],
            expected_pool_size=data["expected_pool_size"],
            expected_yield=data["expected_yield"],
        )
        return TargetingResult(
            recommendation_priority=rec.priority,
            mode="customer_profile",
            customer_profile=profile,
            pr_placements=None,
        )

    # ------------------------------------------------------------------
    elif job.mode == "pr_placement":
        user_msg = (
            f"Generate targeted PR pitches for the following outlets based on "
            f"this AEO recommendation.\n\n"
            f"Priority : {rec.priority}\n"
            f"Category : {rec.category}\n"
            f"Topic    : {rec.topic}\n"
            f"Finding  : {rec.finding}\n"
            f"Action   : {rec.action}\n\n"
            f"Outlets: {', '.join(_PR_OUTLETS)}\n\n"
            f"Rank by audience fit for UK/Ireland accountants and payroll professionals."
        )
        message = await client.messages.create(
            model=_MODEL,
            max_tokens=4096,
            system=_PR_PLACEMENT_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        data = json.loads(_strip_fences(message.content[0].text))

        _fit = {"High": 0, "Medium": 1, "Low": 2}
        placements = sorted(
            [
                PRPlacement(
                    outlet=p["outlet"],
                    citation_frequency=p["citation_frequency"],
                    audience_fit=p["audience_fit"],
                    lead_time=p["lead_time"],
                    pitch_angle=p["pitch_angle"],
                    draft_pitch=p["draft_pitch"],
                    contact_approach=p["contact_approach"],
                )
                for p in data["placements"]
            ],
            key=lambda p: (-p.citation_frequency, _fit.get(p.audience_fit, 3)),
        )
        return TargetingResult(
            recommendation_priority=rec.priority,
            mode="pr_placement",
            customer_profile=None,
            pr_placements=placements,
        )

    # ------------------------------------------------------------------
    else:
        raise ValueError(
            f"Unknown targeting mode '{job.mode}'. "
            f"Valid modes: customer_profile, pr_placement"
        )
