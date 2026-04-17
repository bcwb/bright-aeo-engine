"""
QueryAgent Protocol — the contract every AI query agent must satisfy.

Any module (or object) that exposes a top-level async `query(job)` function
conforming to this signature is a valid QueryAgent.

Adding a new AI model:
  1. Create backend/agents/query_<model>.py implementing `async def query(job)`
  2. Call register() at the bottom of that file
  3. That's it — no changes to the orchestrator needed

Example:
    async def query(job: QueryJob) -> QueryResult:
        ...

    from agents.registry import register
    register(
        name="mymodel",
        env_key="MYMODEL_API_KEY",
        cost_per_token=0.000005,
        module=sys.modules[__name__],
    )
"""

from typing import Protocol

from models import QueryJob, QueryResult


class QueryAgent(Protocol):
    """Structural interface for AI query agent modules."""

    async def query(self, job: QueryJob) -> QueryResult:
        """
        Execute a single AI query job.

        Must return a QueryResult with status='success' or status='error'.
        Must never raise — catch all exceptions and return status='error'.
        """
        ...
