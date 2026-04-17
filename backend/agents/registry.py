"""
QueryAgent registry — maps model names to their agent modules and metadata.

Each agent self-registers by calling register() at module load time.
The orchestrator calls get_active() to discover which agents are available
for a given run — no hardcoded model lists anywhere else.

Usage (in an agent file):
    import sys
    from agents.registry import register
    register("claude", "ANTHROPIC_API_KEY", 0.000060, sys.modules[__name__])

Usage (in the orchestrator):
    from agents import registry
    active = registry.get_active(config, model_filter)
    for reg in active:
        result = await reg.module.query(job)
"""

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentRegistration:
    name: str             # config key, e.g. "claude"
    env_key: str          # environment variable holding the API key
    cost_per_token: float # approximate USD per token (for cost estimation)
    module: Any           # module with async query(job: QueryJob) -> QueryResult


# Module-level registry — populated by each agent on import
_REGISTRY: dict[str, AgentRegistration] = {}


def register(
    name: str,
    env_key: str,
    cost_per_token: float,
    module: Any,
) -> None:
    """Register an agent. Called once per agent at module load time."""
    _REGISTRY[name] = AgentRegistration(
        name=name,
        env_key=env_key,
        cost_per_token=cost_per_token,
        module=module,
    )


def get(name: str) -> AgentRegistration | None:
    return _REGISTRY.get(name)


def all_registrations() -> dict[str, AgentRegistration]:
    return dict(_REGISTRY)


def get_active(config: dict, model_filter: str | None) -> list[AgentRegistration]:
    """Return registrations for models that are:
      - registered
      - enabled in config
      - match model_filter (if set)
      - have a valid API key in the environment
    """
    result: list[AgentRegistration] = []
    model_config: dict = config.get("models", {})

    for name, reg in _REGISTRY.items():
        if name not in model_config:
            continue
        if not model_config[name].get("enabled", True):
            continue
        if model_filter is not None and name != model_filter:
            continue
        if not os.environ.get(reg.env_key):
            continue
        result.append(reg)

    return result
