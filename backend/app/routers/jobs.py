import uuid, magic
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from ..models import JobInfo
from ..services.storage import save_upload
from ..workers.tasks import convert_task, celery

router = APIRouter()

SUPPORTED = {"mp4->mp3","pdf->jpg","jpg->pdf","docx->pdf"}

def _validate(file: UploadFile, target: str):
    if target not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Unsupported target '{target}'. Supported: {sorted(SUPPORTED)}")
    head = file.file.read(8192)
    file.file.seek(0)
    mime = magic.from_buffer(head, mime=True)
    if target == "mp4->mp3" and not (mime.startswith("video/") or file.filename.lower().endswith(".mp4")):
        raise HTTPException(status_code=400, detail=f"Input does not look like a video file (got {mime}).")
    if target in {"jpg->pdf"} and not (mime.startswith("image/") or file.filename.lower().endswith(('.jpg','.jpeg','.png','.webp','.tif','.tiff'))):
        raise HTTPException(status_code=400, detail=f"Input does not look like an image (got {mime}).")
    if target in {"pdf->jpg"} and not (mime == "application/pdf" or file.filename.lower().endswith(".pdf")):
        raise HTTPException(status_code=400, detail=f"Input does not look like a PDF (got {mime}).")
    if target == "docx->pdf" and not (file.filename.lower().endswith(".docx")):
        raise HTTPException(status_code=400, detail="Please upload a .docx file for docx->pdf.")

@router.post("/", response_model=JobInfo)
async def create_job(
    target: str = Form(...),
    file: UploadFile = File(...),
    options: str = Form("{}", description='JSON string with options (e.g., {"dpi":300,"bitrate":"192k"})'),
):
    _validate(file, target)
    job_id = str(uuid.uuid4())
    input_path = save_upload(job_id, file)
    try:
        import json
        opts = json.loads(options) if options else {}
    except Exception:
        opts = {}
    task = convert_task.delay(job_id=job_id, target=target, input_path=str(input_path), options=opts)
    return JobInfo(job_id=task.id, status="queued", progress=0)

@router.get("/{job_id}", response_model=JobInfo)
def get_status(job_id: str):
    async_result = celery.AsyncResult(job_id)
    status_map = {
        "PENDING":"queued",
        "RECEIVED":"processing","STARTED":"processing","RETRY":"processing",
        "SUCCESS":"done","FAILURE":"error"
    }
    try:
        st = status_map.get(async_result.status, "queued")
    except Exception:
        # Fall back if backend has trouble decoding meta
        st = "error"
    info = async_result.info if isinstance(async_result.info, dict) else {}
    # If failed, try to extract message from exception object
    if st == "error" and not info:
        try:
            exc = async_result.result  # may be an Exception
            info = {"error": str(exc)}
        except Exception:
            info = {"error": "Task failed"}
    return JobInfo(
        job_id=job_id,
        status=st,
        progress=info.get("progress", 0),
        download_url=info.get("download_url"),
        error=info.get("error"),
    )
