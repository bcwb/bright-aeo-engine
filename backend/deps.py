"""
Application-level singletons — repositories and services.

Import from here in controllers and main.py to share instances.
"""

from pathlib import Path

from repositories.config_repository import ConfigRepository
from repositories.results_repository import ResultsRepository
from services.config_service import ConfigService
from services.content_service import ContentService
from services.run_service import RunService

# ── Paths ──────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"
RESULTS_DIR = Path(__file__).parent / "results"
ASSETS_DIR  = Path(__file__).parent / "assets"

# ── Repositories ───────────────────────────────────────────────────────────
config_repo  = ConfigRepository(CONFIG_PATH, ASSETS_DIR)
results_repo = ResultsRepository(RESULTS_DIR)

# ── Services ───────────────────────────────────────────────────────────────
config_svc  = ConfigService(config_repo)
run_svc     = RunService(results_repo)
content_svc = ContentService(config_repo, results_repo)
