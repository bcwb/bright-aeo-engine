from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from deps import ASSETS_DIR

router = APIRouter(prefix="/assets", tags=["assets"])


def _resolve(filename: str):
    """Resolve filename to an absolute path, rejecting traversal attempts."""
    filename = (filename or "").strip().lstrip("/")
    if not filename:
        raise HTTPException(status_code=400, detail="file is required")
    path = (ASSETS_DIR / filename).resolve()
    if not str(path).startswith(str(ASSETS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    return path


@router.get("/content")
async def get_asset_content(file: str):
    """Return the text content of an asset file."""
    path = _resolve(file)
    if not path.exists():
        return {"file": file, "content": ""}
    return {"file": file, "content": path.read_text(encoding="utf-8")}


class SaveBody(BaseModel):
    file: str
    content: str


@router.put("/content")
async def save_asset_content(body: SaveBody):
    """Write text content to an asset file, creating parent dirs if needed."""
    path = _resolve(body.file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.content, encoding="utf-8")
    return {"saved": True, "file": body.file}
