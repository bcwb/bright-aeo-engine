"""
AEO Engine — structured logging.

Usage in any module:
    from core.logging import get_logger
    logger = get_logger(__name__)

    logger.info("Run started", extra={"context": {"run_id": run_id, "total_jobs": 27}})

Environment variables:
    LOG_LEVEL   DEBUG | INFO | WARNING | ERROR  (default: INFO)
    LOG_FORMAT  dev | json                       (default: dev)

Dev format  — coloured, human-readable, one or two lines per event.
JSON format — one JSON object per line, for log aggregators (Datadog, CloudWatch, etc.)
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

class _JSONFormatter(logging.Formatter):
    """Machine-readable JSON lines — one event per line."""

    def format(self, record: logging.LogRecord) -> str:
        ctx = getattr(record, "context", {})
        entry: dict = {
            "ts":     datetime.now(timezone.utc).isoformat(),
            "level":  record.levelname,
            "logger": record.name,
            "event":  record.getMessage(),
            **ctx,
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry)


class _DevFormatter(logging.Formatter):
    """Coloured, human-readable output for local development."""

    _COLOURS = {
        "DEBUG":    "\033[36m",   # cyan
        "INFO":     "\033[32m",   # green
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[35m",   # magenta
    }
    _RESET = "\033[0m"
    _DIM   = "\033[2m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self._COLOURS.get(record.levelname, "")
        ctx    = getattr(record, "context", {})

        ts    = datetime.now().strftime("%H:%M:%S")
        level = f"{colour}{record.levelname:<7}{self._RESET}"

        # Prefix with short run_id if present
        run_id = ctx.get("run_id", "")
        prefix = f"{self._DIM}[{str(run_id)[:8]}]{self._RESET} " if run_id else ""

        msg    = record.getMessage()
        line1  = f"{ts}  {level}  {prefix}{msg}"

        # Secondary line: remaining context key=value pairs (skip run_id — already in prefix)
        rest = {k: v for k, v in ctx.items() if k != "run_id"}
        if rest:
            kv    = "  ".join(f"{self._DIM}{k}{self._RESET}={v}" for k, v in rest.items())
            line2 = f"           {prefix}{kv}"
            result = f"{line1}\n{line2}"
        else:
            result = line1

        if record.exc_info:
            result += "\n" + self.formatException(record.exc_info)

        return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_logging() -> None:
    """
    Configure the root 'aeo' logger.
    Call exactly once on application startup (main.py).
    Subsequent calls are no-ops.
    """
    logger = logging.getLogger("aeo")
    if logger.handlers:
        return  # Already configured

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level      = getattr(logging, level_name, logging.INFO)
    fmt        = os.environ.get("LOG_FORMAT", "dev").lower()

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JSONFormatter() if fmt == "json" else _DevFormatter())
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Return a child of the 'aeo' logger, namespaced by module name.

    Example:
        logger = get_logger(__name__)
        # → logging.getLogger("aeo.agents.orchestrator")
    """
    # Strip the package prefix so 'backend.agents.orchestrator' → 'aeo.agents.orchestrator'
    clean = name.removeprefix("backend.").removeprefix("backend/")
    return logging.getLogger(f"aeo.{clean}")
