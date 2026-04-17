"""Query agent for Google Gemini 1.5 Pro."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dotenv import load_dotenv
load_dotenv()

from google import genai
from models import QueryJob, QueryResult
from core.logging import get_logger

logger = get_logger(__name__)

MODEL_STRING = "gemini-1.5-pro"


async def query(job: QueryJob) -> QueryResult:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("API key missing", extra={"context": {
            "model": "gemini", "job_id": job.job_id,
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error="GOOGLE_API_KEY not set", tokens_used=0, latency_ms=0,
        )

    client = genai.Client(api_key=api_key)
    start = time.time()

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_STRING,
            contents=job.prompt,
        )
        response_text = response.text
        tokens_used = (
            response.usage_metadata.total_token_count
            if hasattr(response, "usage_metadata") and response.usage_metadata
            else len(response_text.split())
        )
        latency_ms = int((time.time() - start) * 1000)

        logger.debug("Query ok", extra={"context": {
            "model": "gemini", "job_id": job.job_id,
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
            "model": "gemini", "job_id": job.job_id,
            "prompt": job.prompt[:60], "error": str(e),
        }})
        return QueryResult(
            job_id=job.job_id, prompt=job.prompt, topic=job.topic,
            model=job.model, response_text="", status="error",
            error=str(e), tokens_used=0, latency_ms=latency_ms,
        )
