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
# All keys are optional at startup — models without a key are simply skipped.
# At least one key must be present or there is nothing to run.
_ALL_KEYS = {
    "ANTHROPIC_API_KEY": "Claude",
    "OPENAI_API_KEY":    "GPT-4o",
    "GOOGLE_API_KEY":    "Gemini",
    "PERPLEXITY_API_KEY":"Perplexity",
}
_present = [label for key, label in _ALL_KEYS.items() if os.environ.get(key)]
_missing = [label for key, label in _ALL_KEYS.items() if not os.environ.get(key)]

if not _present:
    raise RuntimeError(
        "\n\nNo API keys are set — at least one is required.\n"
        f"Edit {ROOT / '.env'} and restart.\n"
    )
if _missing:
    print(f"INFO: No key set for {', '.join(_missing)} — those models will be skipped.")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

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

# ── Frontend static files (production) ────────────────────────────────────
# When frontend/dist exists (i.e. after `npm run build`), FastAPI serves the
# React SPA directly.  In local dev, Vite's dev server handles the frontend
# and proxies API calls to this backend, so the dist folder won't exist.
_FRONTEND_DIST = ROOT / "frontend" / "dist"

if _FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    # Serve Vite's hashed JS/CSS assets.  Routers are registered above, so
    # the POST /assets/open endpoint is found before this mount for POST requests.
    if (_FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="vite-assets")

    # Catch-all: return index.html for any path not matched by the API routers
    # above, which lets React Router handle client-side navigation.
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(_FRONTEND_DIST / "index.html")
