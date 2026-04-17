from fastapi import APIRouter

from deps import config_svc

router = APIRouter(prefix="/config", tags=["config"])


@router.get("")
async def get_config():
    return await config_svc.get_config()


@router.post("/prompts", status_code=201)
async def add_prompt(prompt: dict):
    return await config_svc.add_prompt(prompt)


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, updates: dict):
    return await config_svc.update_prompt(prompt_id, updates)


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    return await config_svc.delete_prompt(prompt_id)


@router.post("/competitors", status_code=201)
async def add_competitor(competitor: dict):
    return await config_svc.add_competitor(competitor)


@router.put("/competitors/{competitor_id}")
async def update_competitor(competitor_id: str, updates: dict):
    return await config_svc.update_competitor(competitor_id, updates)


@router.delete("/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str):
    return await config_svc.delete_competitor(competitor_id)


@router.post("/peer_sets", status_code=201)
async def add_peer_set(body: dict):
    return await config_svc.add_peer_set(body.get("label", "").strip())


@router.delete("/peer_sets/{key}")
async def delete_peer_set(key: str):
    return await config_svc.delete_peer_set(key)


@router.put("/benchmark_brand")
async def update_benchmark_brand(body: dict):
    return await config_svc.update_benchmark_brand((body.get("name") or "").strip())


@router.put("/models")
async def update_models(updates: dict):
    return await config_svc.update_models(updates)
