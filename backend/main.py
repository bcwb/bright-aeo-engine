"""
Bright AEO Engine — FastAPI entry point.

Responsibilities:
  - Load environment and validate API keys
  - Configure logging
  - Create the FastAPI app with middleware and the AEOError handler
  - Include all route controllers

Start with:
    cd bright-aeo-engine/backend
    uvicorn main:app --reload --port 8000
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ── API key validation ─────────────────────────────────────────────────────
_REQUIRED_KEYS = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"]
_missing = [k for k in _REQUIRED_KEYS if not os.environ.get(k)]
if _missing:
    raise RuntimeError(
        f"\n\nMissing required API keys: {', '.join(_missing)}\n"
        f"Edit {ROOT / '.env'} and restart.\n"
    )
if not os.environ.get("PERPLEXITY_API_KEY"):
    print("INFO: PERPLEXITY_API_KEY not set — Perplexity queries will be skipped.")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.logging import get_logger, setup_logging
from errors.exceptions import AEOError

setup_logging()
logger = get_logger(__name__)

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(title="Bright AEO Engine", version="1.0.0")


@app.exception_handler(AEOError)
async def aeo_error_handler(request: Request, exc: AEOError) -> JSONResponse:
    """Map any typed AEOError to the correct HTTP status code and JSON body."""
    logger.error(
        f"{exc.__class__.__name__}: {exc}",
        extra={"context": {"path": request.url.path, **exc.context}},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "error_type": exc.__class__.__name__},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Controllers ────────────────────────────────────────────────────────────
from controllers.config_controller import router as config_router
from controllers.run_controller import router as run_router
from controllers.content_controller import router as content_router
from controllers.log_controller import router as log_router
from controllers.asset_controller import router as asset_router

app.include_router(config_router)
app.include_router(run_router)
app.include_router(content_router)
app.include_router(log_router)
app.include_router(asset_router)
