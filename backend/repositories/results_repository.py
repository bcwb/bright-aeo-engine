"""
ResultsRepository — owns all reads and writes to backend/results/*.json.

Usage:
    from repositories.results_repository import ResultsRepository

    repo = ResultsRepository(results_dir)
    data = repo.load(run_id)
    repo.save(run_id, data)
    rows = repo.list_all()                              # sorted by mtime ascending
    item = repo.find_content_item(content_id)           # (run_data, item) | None
"""

import json
from pathlib import Path

from errors.exceptions import RunNotFound


class ResultsRepository:
    """Reads and writes run result JSON files from the results directory."""

    def __init__(self, results_dir: Path) -> None:
        self._dir = results_dir
        self._dir.mkdir(exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self, run_id: str) -> dict:
        path = self._dir / f"{run_id}.json"
        if not path.exists():
            raise RunNotFound(f"Run '{run_id}' not found", context={"run_id": run_id})
        return json.loads(path.read_text())

    def save(self, run_id: str, data: dict) -> None:
        (self._dir / f"{run_id}.json").write_text(
            json.dumps(data, indent=2, default=str)
        )

    def list_all(self) -> list[dict]:
        """Return all run result dicts, sorted by file mtime ascending (oldest first)."""
        paths = sorted(self._dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        rows = []
        for path in paths:
            try:
                rows.append(json.loads(path.read_text()))
            except Exception:
                continue
        return rows

    def find_content_item(self, content_id: str) -> tuple[dict, dict] | None:
        """Scan all run files for a content item with the given content_id.
        Returns (run_data, item) if found, None otherwise."""
        for path in sorted(self._dir.glob("*.json")):
            try:
                data = json.loads(path.read_text())
            except Exception:
                continue
            for item in data.get("content_items", []):
                if item.get("content_id") == content_id:
                    return data, item
        return None
