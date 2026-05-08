import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from agents import orchestrator
from auth import CurrentUser, get_current_user
from core.logging import get_logger
from deps import config_repo, results_repo, run_svc
from errors.exceptions import RunNotFound

router = APIRouter(prefix="/runs", tags=["runs"])
logger = get_logger(__name__)

# SSE state: run_id → asyncio.Queue of progress events
_run_queues: dict[str, asyncio.Queue] = {}


@router.post("", status_code=202)
async def trigger_run(body: dict = {}, user: CurrentUser = Depends(get_current_user)):
    run_id       = str(uuid.uuid4())
    config       = config_repo.load()
    topic_filter = body.get("topic")
    model_filter = body.get("model")
    triggered_by = user.attribution()

    queue: asyncio.Queue = asyncio.Queue()
    _run_queues[run_id] = queue

    async def _run_task():
        try:
            await orchestrator.run_analysis(
                run_id=run_id,
                config=config,
                topic_filter=topic_filter,
                model_filter=model_filter,
                triggered_by=triggered_by,
                progress_callback=queue.put,
            )
        except Exception as e:
            await queue.put({"type": "error", "run_id": run_id, "message": str(e)})

    asyncio.create_task(_run_task())
    logger.info("Run triggered", extra={"context": {
        "run_id":       run_id,
        "topic_filter": topic_filter or "all",
        "model_filter": model_filter or "all",
        "user_email":   user.email,
    }})

    active_prompts = [
        p for p in config["prompts"]
        if p.get("active", True) and (topic_filter is None or p["topic"] == topic_filter)
    ]
    active_models = [
        m for m, cfg in config["models"].items()
        if cfg.get("enabled", True) and (model_filter is None or m == model_filter)
    ]

    return {
        "run_id":      run_id,
        "status":      "running",
        "total_calls": len(active_prompts) * len(active_models),
        "stream_url":  f"/runs/{run_id}/stream",
    }


@router.get("")
async def list_runs():
    return run_svc.list_runs()


@router.get("/{run_id}")
async def get_run(run_id: str):
    return results_repo.load(run_id)


@router.get("/{run_id}/stream")
async def stream_run(run_id: str):
    """SSE endpoint — streams live progress events while the run is active."""

    if run_id not in _run_queues:
        try:
            data = results_repo.load(run_id)
        except RunNotFound:
            raise HTTPException(
                status_code=404,
                detail=f"Run '{run_id}' not found or not yet started",
            )
        analysis = data.get("analysis") or {}

        async def _completed():
            yield f"data: {json.dumps({'type': 'complete', 'run_id': run_id, 'status': data.get('status'), 'bright_overall_rate': analysis.get('bright_overall_rate'), 'total_responses': analysis.get('total_responses', 0), 'failed_calls': analysis.get('failed_calls', 0)})}\n\n"

        return StreamingResponse(
            _completed(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    queue = _run_queues[run_id]

    async def _live_stream():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=25.0)
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
                    continue
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in ("complete", "error"):
                    _run_queues.pop(run_id, None)
                    break
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        _live_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
