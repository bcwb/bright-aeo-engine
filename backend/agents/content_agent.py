"""
Content agent.

Generates channel-specific content for a given Recommendation.
Loads brand assets from /assets, builds a channel-appropriate prompt,
calls Claude API, and returns a structured ContentResult.

Supported channels:
  linkedin | reddit | wikipedia | accountingweb |
  g2_outreach | trustpilot_outreach | pr_pitch | web_page
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from models import ContentJob, ContentResult
from core.logging import get_logger
from errors.exceptions import ChannelNotSupported, MissingAPIKey

logger = get_logger(__name__)

_MODEL = "claude-opus-4-6"

ASSETS_DIR = Path(__file__).parent.parent / "assets"

# Always loaded regardless of topic
_CORE_ASSETS: list[str] = [
    "tone-of-voice.md",
    "customer-proof/stats.md",
    "competitive-positioning.md",
    "customer-proof/case-studies.md",
]

# Channel-specific prompts — verbatim from brief
_CHANNEL_PROMPTS: dict[str, str] = {
    "linkedin": """\
Write a LinkedIn post for Bright Software Group.
150-300 words. Opens with a hook that does not mention the product.
First-person or customer voice. One proof point with a specific number.
Ends with a question to drive engagement.
Maximum 3 relevant hashtags. No direct sales language.
Tone: confident, peer-to-peer, professional but not corporate.""",

    "reddit": """\
Write a Reddit community post for r/UKAccountants or r/payroll.
Written as a genuine community member, not a brand representative.
Never mention Bright in the first paragraph.
Lead with the problem the community is actively discussing.
Introduce BrightPay as one option among several — never the only answer.
Include specific technical detail: MTD, CIS, RTI, bureau workflows, auto enrolment.
Conversational, informal, peer-to-peer register.
This content MUST be reviewed by a human before posting.""",

    "wikipedia": """\
Write a Wikipedia article section for Bright Software Group.
Strictly neutral encyclopaedic tone. Only verifiable facts.
No promotional language. No superlatives.
Structure: company overview, history, products, awards, market.
Include references to: AccountingWEB Software Excellence Awards,
ICB Luca Awards, Deloitte Technology Fast 50 2024.
Written to Wikipedia's notability and verifiability standards.""",

    "accountingweb": """\
Write a contributed article for AccountingWEB.
600-900 words. Bureau-owner perspective, not vendor perspective.
Opens with a problem UK accountants recognise.
Uses accountant language: bureau, practice, payroll run, HMRC, MTD, CIS.
Includes at least one customer quote (use [CUSTOMER QUOTE PLACEHOLDER]
for Seamus to fill with a real quote).
Ends with a practical takeaway, not a product pitch.
Do not write like a press release.""",

    "g2_outreach": """\
Write a short customer outreach email requesting a G2 review.
Maximum 3 sentences.
References the customer's specific journey based on the targeting profile.
Makes a specific ask: "a short review mentioning [specific topics]".
Includes a direct link placeholder: [REVIEW LINK].
Warm, not transactional.""",

    "trustpilot_outreach": """\
Write a short customer outreach email requesting a Trustpilot review.
Maximum 3 sentences.
References the customer's specific journey based on the targeting profile.
Makes a specific ask: "a short review mentioning [specific topics]".
Includes a direct link placeholder: [REVIEW LINK].
Warm, not transactional.""",

    "pr_pitch": """\
Write a PR pitch email.
Subject line = the story angle, not the product name.
One paragraph story hook — why this story, why now.
Three bullet point proof points with numbers.
Clear ask: feature, quote inclusion, or roundup mention.
Under 200 words total.""",

    "web_page": """\
Write an answer page for brightsg.com targeting the specific prompt.
800-1200 words. Structured with H2 and H3 headings.
Directly answers the search query in the first paragraph.
Includes FAQ section with 5 questions an accountant would ask.
Uses schema-friendly structure (question/answer pairs).
Ends with a clear CTA.
Tone: authoritative, helpful, not promotional.""",
}


# ---------------------------------------------------------------------------
# Asset loader
# ---------------------------------------------------------------------------

def load_assets(topic: str, topic_asset_file: str | None = None) -> str:
    """
    Load and combine brand asset files relevant to the given topic.
    Always loads core assets (tone of voice, stats, competitive positioning).
    Adds the topic-specific asset file if one is provided.
    Returns a single string with all content separated by dividers.
    """
    filenames = _CORE_ASSETS + ([topic_asset_file] if topic_asset_file else [])
    sections: list[str] = []

    for filename in filenames:
        path = ASSETS_DIR / filename
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                label = path.stem.replace("-", " ").title()
                sections.append(f"### {label}\n\n{content}")

    if not sections:
        return "No brand assets found. Populate backend/assets/ before running content generation."

    return "\n\n---\n\n".join(sections)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _build_prompt(job: ContentJob, assets_text: str) -> str:
    rec = job.recommendation
    sentiment = (
        "\n".join(f"- {s}" for s in job.sentiment_context)
        if job.sentiment_context
        else "No sentiment data available for this topic."
    )
    channel_instructions = _CHANNEL_PROMPTS[job.channel.lower()]

    return f"""\
You are a content writer for Bright Software Group — a UK/Ireland accounting and
payroll software company serving accountants and payroll bureaux.

You are generating content to improve Bright's AEO (Answer Engine Optimisation)
visibility. The goal is authoritative, helpful content that AI models will cite
when answering questions about payroll and practice management software.

BRAND ASSETS:
{assets_text}

RECOMMENDATION CONTEXT:
Priority : {rec.priority}
Category : {rec.category}
Topic    : {rec.topic}
Finding  : {rec.finding}
Action   : {rec.action}

CURRENT AI NARRATIVE (verbatim snippets from AI model responses):
{sentiment}

CONTENT INSTRUCTIONS:
{channel_instructions}

Generate the content now. Output the content only — no preamble, no commentary."""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def generate_content(job: ContentJob) -> ContentResult:
    """
    Generate channel-specific content for a recommendation.
    Raises ValueError for unknown channels.
    Raises RuntimeError if API key is missing.
    """
    channel = job.channel.lower()

    if channel not in _CHANNEL_PROMPTS:
        raise ChannelNotSupported(
            f"Channel '{channel}' is not supported",
            context={"channel": channel, "valid_channels": sorted(_CHANNEL_PROMPTS.keys())},
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise MissingAPIKey("ANTHROPIC_API_KEY not set", context={"agent": "content_agent"})

    assets_text = load_assets(job.recommendation.topic, job.topic_asset_file)
    logger.debug("Assets loaded", extra={"context": {
        "channel": channel, "topic": job.recommendation.topic,
        "topic_asset": job.topic_asset_file or "none",
    }})

    prompt = _build_prompt(job, assets_text)

    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model=_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text.strip()
    word_count = len(content.split())

    logger.info("Content generated", extra={"context": {
        "channel": channel, "rec_priority": job.recommendation.priority,
        "topic": job.recommendation.topic, "word_count": word_count,
    }})

    return ContentResult(
        recommendation_priority=job.recommendation.priority,
        channel=channel,
        content=content,
        word_count=word_count,
        human_review_required=(channel == "reddit"),
        reviewer_name=None,
        reviewer_date=None,
        status="draft",
    )
