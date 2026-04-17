"""Query agent for Anthropic Claude."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

import anthropic
from models import QueryJob, QueryResult
from core.logging import get_logger

logger = get_logger(__name__)

MODEL_STRING = "claude-opus-4-6"


async def query(job: QueryJob) -> QueryResult:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("API key missing", extra={"context": {
            "model": "claude", "job_id": job.job_id,
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error="ANTHROPIC_API_KEY not set", tokens_used=0, latency_ms=0,
        )

    client = anthropic.AsyncAnthropic(api_key=api_key)
    start = time.time()

    try:
        message = await client.messages.create(
            model=MODEL_STRING,
            max_tokens=2048,
            messages=[{"role": "user", "content": job.prompt}],
        )
        response_text = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        latency_ms = int((time.time() - start) * 1000)

        logger.debug("Query ok", extra={"context": {
            "model": "claude", "job_id": job.job_id,
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
            "model": "claude", "job_id": job.job_id,
            "prompt": job.prompt[:60], "error": str(e),
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error=str(e), tokens_used=0, latency_ms=latency_ms,
        )
