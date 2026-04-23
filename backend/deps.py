"""
Application-level singletons — repositories and services.

Import from here in controllers and main.py to share instances.
"""

import os
from pathlib import Path

from repositories.config_repository import ConfigRepository
from repositories.results_repository import ResultsRepository
from services.config_service import ConfigService
from services.content_service import ContentService
from services.run_service import RunService

# ── Paths ──────────────────────────────────────────────────────────────────
# CONFIG_PATH and RESULTS_DIR can be overridden via env vars so that on
# Azure App Service they point to /home/data/ (persistent storage) rather
# than the deployment package directory which is overwritten on each deploy.
_backend = Path(__file__).parent
CONFIG_PATH = Path(os.environ.get("CONFIG_PATH", _backend / "config.json"))
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", _backend / "results"))
ASSETS_DIR  = _backend / "assets"

# ── Repositories ───────────────────────────────────────────────────────────
config_repo  = ConfigRepository(CONFIG_PATH, ASSETS_DIR)
results_repo = ResultsRepository(RESULTS_DIR)

# ── Services ───────────────────────────────────────────────────────────────
config_svc  = ConfigService(config_repo)
run_svc     = RunService(results_repo)
content_svc = ContentService(config_repo, results_repo)
