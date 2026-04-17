from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Query layer
# ---------------------------------------------------------------------------

@dataclass
class QueryJob:
    job_id: str           # uuid4
    prompt: str
    topic: str
    model: str            # "claude" | "openai" | "gemini" | "perplexity"
    peer_set: list[str]   # brand names to detect


@dataclass
class QueryResult:
    job_id: str
    prompt: str
    topic: str
    model: str
    response_text: str
    status: str           # "success" | "error"
    error: str | None
    tokens_used: int
    latency_ms: int


# ---------------------------------------------------------------------------
# Analysis layer
# ---------------------------------------------------------------------------

@dataclass
class BrandCitation:
    brand: str
    count: int
    rate: float           # count / total_responses
    positions: list[int]  # ordinal position of first mention in each response
    sentiment_snippets: list[str]  # sentences containing brand mention


@dataclass
class AnalysisOutput:
    run_date: str         # ISO date
    total_prompts: int
    total_responses: int
    failed_calls: int
    brand_citations: dict[str, BrandCitation]
    by_topic: dict[str, dict[str, BrandCitation]]
    by_model: dict[str, dict[str, BrandCitation]]
    benchmark_brand: str
    bright_overall_rate: float   # citation rate for benchmark_brand (kept for backward compat)
    watchouts: list[str]  # topics/models where benchmark brand citation rate = 0%
    estimated_cost_usd: float


# ---------------------------------------------------------------------------
# Recommendations layer
# ---------------------------------------------------------------------------

@dataclass
class Recommendation:
    priority: int
    category: str   # "Content Gap" | "Narrative Risk" | "Technical" | "Domain Authority" | "Review Signal"
    topic: str
    finding: str
    action: str
    effort: str     # "Low" | "Medium" | "High"
    impact: str     # "Low" | "Medium" | "High"
    timeframe: str
    channels: list[str]  # which channels content should be produced for


@dataclass
class RecommendationsOutput:
    run_id: str
    summary: str
    recommendations: list[Recommendation]


# ---------------------------------------------------------------------------
# Content layer
# ---------------------------------------------------------------------------

@dataclass
class ContentJob:
    recommendation: Recommendation
    channel: str    # "linkedin" | "reddit" | "wikipedia" | "accountingweb" |
                    # "g2_outreach" | "trustpilot_outreach" | "pr_pitch" | "web_page"
    brand_assets: dict  # loaded from /assets folder
    sentiment_context: list[str]  # snippets from analysis showing current narrative
    topic_asset_file: str | None = None  # relative path within ASSETS_DIR for topic-specific asset


@dataclass
class ContentResult:
    recommendation_priority: int
    channel: str
    content: str
    word_count: int
    human_review_required: bool   # always True for reddit
    reviewer_name: str | None     # must be filled before export
    reviewer_date: str | None
    status: str  # "draft" | "reviewed" | "approved" | "posted"


# ---------------------------------------------------------------------------
# Targeting layer
# ---------------------------------------------------------------------------

@dataclass
class TargetingJob:
    recommendation: Recommendation
    mode: str  # "customer_profile" | "pr_placement"


@dataclass
class CustomerProfile:
    product: str
    role_titles: list[str]
    company_type: str
    company_size_range: str
    migration_window: str
    crm_query: str        # plain English query for Seamus to run
    outreach_template: str
    review_ask: str
    expected_pool_size: str
    expected_yield: str


@dataclass
class PRPlacement:
    outlet: str
    citation_frequency: int   # from analysis data
    audience_fit: str         # "High" | "Medium" | "Low"
    lead_time: str
    pitch_angle: str
    draft_pitch: str
    contact_approach: str


@dataclass
class TargetingResult:
    recommendation_priority: int
    mode: str
    customer_profile: CustomerProfile | None
    pr_placements: list[PRPlacement] | None
