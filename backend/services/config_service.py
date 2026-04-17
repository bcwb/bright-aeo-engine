"""
ConfigService — all business logic for reading and mutating application config.

Raises typed AEOErrors; never raises HTTPException.
Owns the asyncio.Lock that serialises concurrent config writes.

Usage:
    from services.config_service import ConfigService
    from repositories.config_repository import ConfigRepository

    svc = ConfigService(ConfigRepository(config_path, assets_dir))
    config = await svc.get_config()
    prompt = await svc.add_prompt({"topic": "payroll", "text": "..."})
"""

import asyncio
import uuid

from core.logging import get_logger
from errors.exceptions import (
    ConfigError,
    CompetitorNotFound,
    PeerSetAlreadyExists,
    PeerSetNotFound,
    PromptNotFound,
)
from repositories.config_repository import ConfigRepository

logger = get_logger(__name__)


class ConfigService:
    def __init__(self, repo: ConfigRepository) -> None:
        self._repo = repo
        self._lock = asyncio.Lock()

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_config(self) -> dict:
        config = self._repo.load()
        changed = self._repo.ensure_peer_sets(config)
        changed |= self._repo.ensure_topic_assets(config)
        if changed:
            self._repo.save(config)
        return config

    # ── Prompts ───────────────────────────────────────────────────────────────

    async def add_prompt(self, prompt: dict) -> dict:
        async with self._lock:
            config = self._repo.load()
            if not prompt.get("id"):
                prompt["id"] = str(uuid.uuid4())[:8]
            prompt.setdefault("active", True)
            config["prompts"].append(prompt)
            self._repo.ensure_peer_sets(config)
            self._repo.ensure_topic_assets(config)
            self._repo.save(config)
        logger.info("Config changed", extra={"context": {
            "change_type": "add_prompt",
            "entity_id":   prompt["id"],
            "topic":       prompt.get("topic"),
            "text":        prompt.get("text", "")[:60],
        }})
        return prompt

    async def update_prompt(self, prompt_id: str, updates: dict) -> dict:
        async with self._lock:
            config = self._repo.load()
            for p in config["prompts"]:
                if p["id"] == prompt_id:
                    p.update(updates)
                    self._repo.ensure_peer_sets(config)
                    self._repo.ensure_topic_assets(config)
                    self._repo.save(config)
                    return p
        raise PromptNotFound(
            f"Prompt '{prompt_id}' not found", context={"prompt_id": prompt_id}
        )

    async def delete_prompt(self, prompt_id: str) -> dict:
        async with self._lock:
            config = self._repo.load()
            before = len(config["prompts"])
            config["prompts"] = [p for p in config["prompts"] if p["id"] != prompt_id]
            if len(config["prompts"]) == before:
                raise PromptNotFound(
                    f"Prompt '{prompt_id}' not found", context={"prompt_id": prompt_id}
                )
            self._repo.save(config)
        logger.info("Config changed", extra={"context": {
            "change_type": "delete_prompt", "entity_id": prompt_id,
        }})
        return {"deleted": prompt_id}

    # ── Competitors ───────────────────────────────────────────────────────────

    async def add_competitor(self, competitor: dict) -> dict:
        peer_set = competitor.get("peer_set", "payroll")
        async with self._lock:
            config = self._repo.load()
            if peer_set not in config["peer_sets"]:
                raise PeerSetNotFound(
                    f"Unknown peer_set '{peer_set}'", context={"peer_set": peer_set}
                )
            if not competitor.get("id"):
                competitor["id"] = str(uuid.uuid4())[:8]
            competitor.setdefault("variants", [competitor.get("name", "")])
            config["peer_sets"][peer_set].append(competitor)
            self._repo.save(config)
        return competitor

    async def update_competitor(self, competitor_id: str, updates: dict) -> dict:
        async with self._lock:
            config = self._repo.load()
            for peers in config["peer_sets"].values():
                for c in peers:
                    if c["id"] == competitor_id:
                        for k, v in updates.items():
                            if k != "id":
                                c[k] = v
                        self._repo.save(config)
                        return c
        raise CompetitorNotFound(
            f"Competitor '{competitor_id}' not found",
            context={"competitor_id": competitor_id},
        )

    async def delete_competitor(self, competitor_id: str) -> dict:
        async with self._lock:
            config = self._repo.load()
            for set_name, peers in config["peer_sets"].items():
                before = len(peers)
                config["peer_sets"][set_name] = [c for c in peers if c["id"] != competitor_id]
                if len(config["peer_sets"][set_name]) < before:
                    self._repo.save(config)
                    logger.info("Config changed", extra={"context": {
                        "change_type": "delete_competitor",
                        "entity_id":   competitor_id,
                        "peer_set":    set_name,
                    }})
                    return {"deleted": competitor_id}
        raise CompetitorNotFound(
            f"Competitor '{competitor_id}' not found",
            context={"competitor_id": competitor_id},
        )

    # ── Peer sets ─────────────────────────────────────────────────────────────

    async def add_peer_set(self, label: str) -> dict:
        if not label:
            raise ConfigError("label is required")
        key = label.lower().replace(" ", "_").replace("-", "_")
        async with self._lock:
            config = self._repo.load()
            if key in config["peer_sets"]:
                raise PeerSetAlreadyExists(
                    f"Peer set '{key}' already exists", context={"key": key}
                )
            config["peer_sets"][key] = []
            self._repo.save(config)
        return {"key": key, "label": label}

    async def delete_peer_set(self, key: str) -> dict:
        async with self._lock:
            config = self._repo.load()
            if key not in config["peer_sets"]:
                raise PeerSetNotFound(
                    f"Peer set '{key}' not found", context={"key": key}
                )
            del config["peer_sets"][key]
            self._repo.save(config)
        return {"deleted": key}

    # ── Models / benchmark brand ──────────────────────────────────────────────

    async def update_benchmark_brand(self, name: str) -> dict:
        if not name:
            raise ConfigError("name is required")
        async with self._lock:
            config = self._repo.load()
            previous = config.get("benchmark_brand", "Bright")
            config["benchmark_brand"] = name
            self._repo.save(config)
        logger.info("Config changed", extra={"context": {
            "change_type": "update_benchmark_brand",
            "previous":    previous,
            "new":         name,
        }})
        return {"benchmark_brand": name}

    async def update_models(self, updates: dict) -> dict:
        async with self._lock:
            config = self._repo.load()
            for model_name, model_cfg in updates.items():
                if model_name in config["models"]:
                    config["models"][model_name].update(model_cfg)
            self._repo.save(config)
        return self._repo.load()["models"]
