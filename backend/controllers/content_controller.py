from fastapi import APIRouter

from deps import content_svc, results_repo
from errors.exceptions import RecommendationsNotFound

router = APIRouter(tags=["content"])


@router.get("/recommendations/{run_id}")
async def get_recommendations(run_id: str):
    data = results_repo.load(run_id)
    recs = data.get("recommendations")
    if not recs:
        error = data.get("recommendations_error")
        msg = f"No recommendations for run '{run_id}'"
        if error:
            msg += f". Generation failed: {error}"
        raise RecommendationsNotFound(msg, context={"run_id": run_id})
    return recs


@router.post("/content", status_code=202)
async def trigger_content(body: dict):
    return await content_svc.trigger_content(body)


@router.get("/content/{run_id}")
async def get_content(run_id: str):
    return content_svc.get_content(run_id)


@router.put("/content/{content_id}/approve")
async def approve_content(content_id: str, body: dict):
    return await content_svc.approve_content(
        content_id, (body.get("reviewer_name") or "").strip()
    )


@router.get("/targeting/{run_id}")
async def get_targeting(run_id: str):
    return content_svc.get_targeting(run_id)
