from fastapi import APIRouter

from core.logging import get_logger, log_buffer
from errors.exceptions import ConfigError

router = APIRouter(prefix="/logs", tags=["logs"])
logger = get_logger(__name__)

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@router.get("")
async def get_logs(level: str | None = None, limit: int = 200):
    """Return recent log events from the in-memory buffer, newest first."""
    events = log_buffer.get_all()
    if level:
        lvl = level.upper()
        if lvl not in _VALID_LEVELS:
            raise ConfigError(
                f"Invalid log level '{level}'. Valid: {sorted(_VALID_LEVELS)}"
            )
        events = [e for e in events if e.get("level") == lvl]
    limit = min(max(1, limit), 500)
    return list(reversed(events))[:limit]


@router.delete("", status_code=204)
async def clear_logs():
    log_buffer.clear()
    logger.info("Log buffer cleared", extra={"context": {}})
