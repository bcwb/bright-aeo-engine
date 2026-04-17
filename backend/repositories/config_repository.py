"""
ConfigRepository — owns all reads and writes to config.json and topic asset files.

Usage:
    from repositories.config_repository import ConfigRepository

    repo = ConfigRepository(config_path, assets_dir)
    config = repo.load()
    repo.save(config)
"""

import json
from pathlib import Path


_LEGACY_TOPIC_FILES: dict[str, str] = {
    "payroll":             "product-descriptions/brightpay-cloud.md",
    "practice_management": "product-descriptions/brightmanager.md",
    "tax_compliance":      "product-descriptions/brighttax.md",
    "cloud_accounting":    "product-descriptions/brightaccounts.md",
}

_TOPIC_ASSET_TEMPLATE = """\
# {topic} — Topic Brand Assets

> Auto-generated when topic '{topic}' was added.
> Populate this file with product and domain details before generating content.
> The content agent loads this file for every content generation request on this topic.

## What to include

- What this product / solution does (2–3 sentences, plain language)
- Key features relevant to UK/Ireland accountants and payroll bureaux
- Ideal customer profile for this topic area
- Specific proof points with numbers (only include verified figures)
- Awards and recognition relevant to this product
- How Bright differentiates from competitors in this space

## Content

[Populate this section — the more specific the detail, the better the generated content]
"""


class ConfigRepository:
    """Reads and writes config.json; maintains peer sets and topic asset files."""

    def __init__(self, config_path: Path, assets_dir: Path) -> None:
        self._config_path = config_path
        self._assets_dir = assets_dir

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self) -> dict:
        return json.loads(self._config_path.read_text())

    def save(self, config: dict) -> None:
        self._config_path.write_text(json.dumps(config, indent=2))

    def ensure_peer_sets(self, config: dict) -> bool:
        """Create an empty peer set for any topic that doesn't have one yet.
        Returns True if the config was modified."""
        changed = False
        for prompt in config.get("prompts", []):
            topic = prompt.get("topic", "").strip()
            if not topic:
                continue
            key = self.topic_to_key(topic)
            if key not in config["peer_sets"]:
                config["peer_sets"][key] = []
                changed = True
        return changed

    def ensure_topic_assets(self, config: dict) -> bool:
        """Create a topic asset .md file and config mapping for any topic without one.
        Returns True if the config was modified."""
        if "topic_assets" not in config:
            config["topic_assets"] = {}
        changed = False
        seen: set[str] = set()
        for prompt in config.get("prompts", []):
            topic = prompt.get("topic", "").strip()
            if not topic or topic in seen:
                continue
            seen.add(topic)
            key = self.topic_to_key(topic)
            if key in config["topic_assets"]:
                continue
            filename = _LEGACY_TOPIC_FILES.get(key, f"product-descriptions/{key}.md")
            path = self._assets_dir / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(_TOPIC_ASSET_TEMPLATE.format(topic=topic), encoding="utf-8")
            config["topic_assets"][key] = filename
            changed = True
        return changed

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def topic_to_key(topic: str) -> str:
        return topic.strip().lower().replace(" ", "_").replace("-", "_")
