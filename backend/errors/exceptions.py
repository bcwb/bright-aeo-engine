"""
AEO Engine — typed exception hierarchy.

All exceptions inherit from AEOError which carries:
  - message  : human-readable description
  - context  : optional dict of structured data for logging
  - status_code : default HTTP status code for this exception type

Usage in agents and services:
    raise LLMParseError("Recommendations returned invalid JSON", context={"raw": raw[:200]})

Usage in controllers (once Phase 5 is complete, or in main.py now):
    @app.exception_handler(AEOError)
    async def aeo_error_handler(request, exc):
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

Hierarchy:

    AEOError
    ├── ConfigError           400
    │   ├── PromptNotFound    404
    │   ├── CompetitorNotFound 404
    │   ├── PeerSetNotFound   404
    │   └── PeerSetAlreadyExists 409
    ├── RunError              422
    │   ├── RunNotFound       404
    │   ├── NoActivePrompts   422
    │   └── NoActiveModels    422
    ├── ContentError          400
    │   └── ChannelNotSupported 400
    └── AgentError            500
        ├── LLMParseError     500
        └── MissingAPIKey     500
"""


class AEOError(Exception):
    """Base class for all AEO Engine exceptions."""

    status_code: int = 500

    def __init__(self, message: str, context: dict | None = None) -> None:
        super().__init__(message)
        self.context: dict = context or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)!r})"


# ---------------------------------------------------------------------------
# Config errors
# ---------------------------------------------------------------------------

class ConfigError(AEOError):
    """A configuration operation failed."""
    status_code = 400


class PromptNotFound(ConfigError):
    """No prompt with the given ID exists in config."""
    status_code = 404


class CompetitorNotFound(ConfigError):
    """No competitor with the given ID exists in any peer set."""
    status_code = 404


class PeerSetNotFound(ConfigError):
    """No peer set with the given key exists in config."""
    status_code = 404


class PeerSetAlreadyExists(ConfigError):
    """A peer set with this key already exists."""
    status_code = 409


# ---------------------------------------------------------------------------
# Run errors
# ---------------------------------------------------------------------------

class RunError(AEOError):
    """A run operation failed."""
    status_code = 422


class RunNotFound(RunError):
    """No result file exists for the given run ID."""
    status_code = 404


class RecommendationsNotFound(RunError):
    """The run exists but recommendations have not been generated yet."""
    status_code = 404


class NoActivePrompts(RunError):
    """The run was started but no prompts match the current filter."""
    status_code = 422


class NoActiveModels(RunError):
    """The run was started but no models are enabled or have valid API keys."""
    status_code = 422


# ---------------------------------------------------------------------------
# Content errors
# ---------------------------------------------------------------------------

class ContentError(AEOError):
    """A content generation operation failed."""
    status_code = 400


class ChannelNotSupported(ContentError):
    """The requested content channel is not in the valid set."""
    status_code = 400


class ContentItemNotFound(ContentError):
    """No content item with the given ID exists in any run."""
    status_code = 404


# ---------------------------------------------------------------------------
# Agent errors (AI integration layer)
# ---------------------------------------------------------------------------

class AgentError(AEOError):
    """
    An AI agent encountered an unrecoverable error.
    These are caught by the orchestrator / main.py and stored in the result
    file — they do not abort the run unless all models fail.
    """
    status_code = 500


class LLMParseError(AgentError):
    """
    An LLM returned a response that could not be parsed into the expected schema.
    Raised by: recommender, content_agent, targeting_agent.
    """
    status_code = 500


class MissingAPIKey(AgentError):
    """
    A required API key is not set in the environment.
    Raised by LLM agents (recommender, content_agent, targeting_agent) when
    the key is needed for a non-query operation where failing silently is wrong.
    Query agents return a QueryResult(status='error') instead of raising.
    """
    status_code = 500
