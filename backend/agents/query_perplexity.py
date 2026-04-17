"""Query agent for Perplexity (llama-3.1-sonar-large-128k-online).

Uses a direct HTTP POST — Perplexity has no official Python SDK.
This is intentionally the most important model for AEO measurement
because it performs live web search, reflecting current indexed content.
"""

import os
import sys
import time

from agents.registry import register as _register

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

import httpx
from models import QueryJob, QueryResult
from core.logging import get_logger

logger = get_logger(__name__)

MODEL_STRING = "llama-3.1-sonar-large-128k-online"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


async def query(job: QueryJob) -> QueryResult:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        logger.warning("API key missing", extra={"context": {
            "model": "perplexity", "job_id": job.job_id,
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error="PERPLEXITY_API_KEY not set", tokens_used=0, latency_ms=0,
        )

    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL_STRING,
                    "messages": [{"role": "user", "content": job.prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()

        response_text = data["choices"][0]["message"]["content"]
        tokens_used = data.get("usage", {}).get("total_tokens", 0)
        latency_ms = int((time.time() - start) * 1000)

        logger.debug("Query ok", extra={"context": {
            "model": "perplexity", "job_id": job.job_id,
            "prompt": job.prompt[:60], "latency_ms": latency_ms,
            "tokens": tokens_used,
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text=response_text, status="success",
            error=None, tokens_used=tokens_used, latency_ms=latency_ms,
        )
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        logger.warning("Query failed", extra={"context": {
            "model": "perplexity", "job_id": job.job_id,
            "prompt": job.prompt[:60], "error": str(e),
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error=str(e), tokens_used=0, latency_ms=latency_ms,
        )


_register("perplexity", "PERPLEXITY_API_KEY", 0.000001, sys.modules[__name__])
