"""
Recommendations agent.

Accepts an AnalysisOutput and returns a RecommendationsOutput.
Calls Claude API with the AEO specialist system prompt defined in the brief.
Returns only valid JSON — raises RuntimeError on malformed responses.
"""

import dataclasses
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from models import AnalysisOutput, Recommendation, RecommendationsOutput
from core.logging import get_logger
from errors.exceptions import LLMParseError, MissingAPIKey

logger = get_logger(__name__)

_MODEL = "claude-opus-4-6"

# Verbatim from brief — do not edit without updating the brief.
_SYSTEM_PROMPT = """\
You are an AEO (Answer Engine Optimisation) specialist
analysing AI visibility data for Bright Software Group —
a UK/Ireland accounting and payroll software business
serving accountants, payroll bureaux, and practices.

Bright's ICP is UK/Ireland accountants and payroll bureaux,
NOT direct SME buyers. Do not recommend visibility
improvements in generic SME accounting categories.

You will receive structured analysis data. Generate specific,
actionable recommendations that will improve Bright's AI
visibility over the next 30-90 days.

Rules:
- Work ONLY from the topics and query results present in the analysis
  data. Do not infer or recommend about topics, products, or categories
  that are not represented in the data you receive.
- Every recommendation must name a specific action, not a direction
- Prioritise by commercial impact
- Quick wins (under 1 week, no new resource) should appear in priority 1-3
- Where sentiment snippets show negative narrative (pricing, migration
  concerns), recommend specific content to counter it on the exact
  platforms AI models are citing
- Reference specific competitor names where they dominate a topic Bright should own
- Include a channels list for each recommendation — pick from the
  EXACT values below only, no other values are permitted:
    "linkedin" | "reddit" | "wikipedia" | "accountingweb" |
    "g2_outreach" | "trustpilot_outreach" | "pr_pitch" | "web_page"
- Do not recommend generic SEO improvements — every action must be
  specific enough to brief tomorrow

Return ONLY valid JSON. No preamble. No markdown fences.
Schema: { "summary": string, "recommendations": [Recommendation] }

Where each Recommendation object has these exact fields:
{
  "priority": integer,
  "category": "Content Gap" | "Narrative Risk" | "Technical" | "Domain Authority" | "Review Signal",
  "topic": string,
  "finding": string,
  "action": string,
  "effort": "Low" | "Medium" | "High",
  "impact": "Low" | "Medium" | "High",
  "timeframe": string,
  "channels": ["linkedin" | "reddit" | "wikipedia" | "accountingweb" | "g2_outreach" | "trustpilot_outreach" | "pr_pitch" | "web_page"]
}\
"""


async def generate_recommendations(
    analysis: AnalysisOutput, run_id: str, topic_filter: str | None = None
) -> RecommendationsOutput:
    """
    Call Claude API with AEO specialist prompt + serialised analysis data.
    Returns structured RecommendationsOutput.
    Raises RuntimeError if Claude returns malformed JSON.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise MissingAPIKey("ANTHROPIC_API_KEY not set", context={"agent": "recommender"})

    logger.info("Generating recommendations", extra={"context": {
        "run_id": run_id, "topic_filter": topic_filter or "all",
        "total_responses": analysis.total_responses,
    }})

    client = anthropic.AsyncAnthropic(api_key=api_key)

    analysis_payload = json.dumps(dataclasses.asdict(analysis), indent=2)

    # Build scope note so the model doesn't recommend improvements for topics
    # not present in this run (e.g. don't recommend BrightManager visibility
    # fixes when running a Payroll-only analysis).
    covered_topics = list(analysis.by_topic.keys()) if analysis.by_topic else []
    if topic_filter:
        scope_note = (
            f"\n\nSCOPE CONSTRAINT: This run queried ONLY '{topic_filter}' prompts. "
            f"Every recommendation must relate directly to improving Bright's visibility "
            f"in '{topic_filter}' queries. Do not generate any recommendation that "
            f"references, implies, or concerns any other product category or topic — "
            f"even if you are aware such products exist. Treat the data above as the "
            f"complete universe of what this run measured."
        )
    elif covered_topics:
        scope_note = (
            f"\n\nSCOPE CONSTRAINT: This run covered only these topics: {', '.join(covered_topics)}. "
            f"Every recommendation must relate directly to one of these topics. "
            f"Do not generate recommendations about any topic or product category "
            f"not represented in the analysis data above."
        )
    else:
        scope_note = ""

    message = await client.messages.create(
        model=_MODEL,
        max_tokens=8192,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Analyse this AEO visibility data for Bright Software Group "
                    "and generate prioritised recommendations:\n\n"
                    f"{analysis_payload}"
                    f"{scope_note}"
                ),
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences if Claude wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Recommendations parse failed", extra={"context": {
            "run_id": run_id, "error": str(exc), "raw_response": raw[:200],
        }})
        raise LLMParseError(
            f"Recommendations agent returned invalid JSON: {exc}",
            context={"run_id": run_id, "raw_response": raw[:500]},
        ) from exc

    recommendations = [
        Recommendation(
            priority=rec["priority"],
            category=rec["category"],
            topic=rec["topic"],
            finding=rec["finding"],
            action=rec["action"],
            effort=rec["effort"],
            impact=rec["impact"],
            timeframe=rec["timeframe"],
            channels=rec["channels"],
        )
        for rec in data["recommendations"]
    ]

    return RecommendationsOutput(
        run_id=run_id,
        summary=data["summary"],
        recommendations=recommendations,
    )
