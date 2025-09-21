import shutil, os, time, uuid, zipfile
from pathlib import Path
from fastapi import UploadFile
from ..config import settings

BASE = settings.storage_dir

def job_dir(job_id: str) -> Path:
    p = BASE / job_id
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_upload(job_id: str, file: UploadFile) -> Path:
    safe_name = file.filename.replace('/', '_').replace('..', '.')
    p = job_dir(job_id) / f"input_{safe_name}"
    with open(p, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return p

def make_output_path(job_id: str, ext: str, name: str = "output") -> Path:
    p = job_dir(job_id) / f"{name}.{ext.lstrip('.')}"
    return p

def presign_download(path: Path) -> str:
    rel = path.relative_to(BASE)
    return f"/files/{rel.as_posix()}"

def package_single_or_zip(job_id: str, files: list[Path], zip_name: str = "output") -> Path:
    """If one file, return it. If many, zip them into job dir and return the zip path."""
    if not files:
        raise RuntimeError("No output files produced")
    if len(files) == 1:
        return files[0]
    # multi → zip
    jd = job_dir(job_id)
    zip_path = jd / f"{zip_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            # put only the basename into zip
            z.write(f, arcname=f.name)
    return zip_path
