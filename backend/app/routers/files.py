from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from ..config import settings

router = APIRouter()

BASE = Path(settings.storage_dir).resolve()

def _safe_path(relpath: str) -> Path:
    # Prevent path traversal by resolving and ensuring it's under BASE
    candidate = (BASE / relpath).resolve()
    if not str(candidate).startswith(str(BASE)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return candidate

@router.get("/files/{relpath:path}")
async def download(relpath: str):
    file_path = _safe_path(relpath)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    # Force download via Content-Disposition: attachment
    return FileResponse(
        path=file_path,
        filename=file_path.name,  # triggers attachment behavior
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_path.name}"}
    )
