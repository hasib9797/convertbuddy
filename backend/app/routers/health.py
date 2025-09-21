from fastapi import APIRouter
router = APIRouter()

@router.get("/live")
def live():
    return {"ok": True}

@router.get("/ready")
def ready():
    return {"ok": True}
