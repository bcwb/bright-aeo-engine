import subprocess

from fastapi import APIRouter, HTTPException

from deps import ASSETS_DIR

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/open")
async def open_asset(body: dict):
    """Open a brand asset file in the system default editor (macOS: `open`)."""
    filename = (body.get("file") or "").strip().lstrip("/")
    if not filename:
        raise HTTPException(status_code=400, detail="file is required")
    path = (ASSETS_DIR / filename).resolve()
    # Security: reject paths that escape the assets directory
    if not str(path).startswith(str(ASSETS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Asset '{filename}' not found")
    subprocess.Popen(["open", str(path)])
    return {"opened": filename}
