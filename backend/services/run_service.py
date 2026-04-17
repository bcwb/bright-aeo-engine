"""
RunService — business logic for querying run results.

The run trigger and SSE streaming remain in main.py (infrastructure concerns).
This service handles result assembly and run-name generation.

Usage:
    from services.run_service import RunService
    from repositories.results_repository import ResultsRepository

    svc = RunService(ResultsRepository(results_dir))
    rows = svc.list_runs()
"""

from collections import Counter

from repositories.results_repository import ResultsRepository


class RunService:
    def __init__(self, repo: ResultsRepository) -> None:
        self._repo = repo

    def list_runs(self) -> list[dict]:
        """Return all completed runs as summary rows, newest first.

        Each row includes a human-readable run_name built from date, scope, and
        citation rate. Duplicate (date, scope) pairs get a v1/v2 version suffix.
        """
        rows: list[dict] = []
        for data in self._repo.list_all():
            analysis = data.get("analysis") or {}

            # Slim by_topic to just the citation rate — full data lives in the run file
            by_topic_raw = analysis.get("by_topic") or {}
            by_topic = {
                topic: {
                    brand: {"rate": bdata.get("rate", 0)}
                    for brand, bdata in brands.items()
                }
                for topic, brands in by_topic_raw.items()
            }

            rows.append({
                "run_id":             data.get("run_id"),
                "run_date":           data.get("run_date"),
                "status":             data.get("status"),
                "topic_filter":       data.get("topic_filter"),
                "model_filter":       data.get("model_filter"),
                "total_prompts":      analysis.get("total_prompts", 0),
                "total_responses":    analysis.get("total_responses", 0),
                "failed_calls":       analysis.get("failed_calls", 0),
                "bright_overall_rate": analysis.get("bright_overall_rate"),
                "watchout_count":     len(analysis.get("watchouts", [])),
                "estimated_cost_usd": (data.get("meta") or {}).get("estimated_cost_usd"),
                "duration_seconds":   (data.get("meta") or {}).get("duration_seconds"),
                "by_topic":           by_topic,
            })

        # Build run_name: count (date, scope) pairs so duplicates get v1/v2 suffix
        pair_counts: Counter = Counter(
            (r["run_date"], r["topic_filter"] or "All topics") for r in rows
        )
        pair_seen: Counter = Counter()

        for r in rows:
            scope = r["topic_filter"] or "All topics"
            key   = (r["run_date"], scope)
            pair_seen[key] += 1

            rate = (
                f"{round(r['bright_overall_rate'] * 100)}% cited"
                if r["bright_overall_rate"] is not None
                else r["status"]
            )

            if pair_counts[key] > 1:
                r["run_name"] = f"{r['run_date']} — {scope} v{pair_seen[key]} — {rate}"
            else:
                r["run_name"] = f"{r['run_date']} — {scope} — {rate}"

        rows.reverse()  # newest first
        return rows
