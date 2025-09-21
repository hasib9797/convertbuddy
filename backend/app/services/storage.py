import zipfile
from pathlib import Path
from typing import Iterable, List
from .storage_backend import get_storage_backend
from ..config import settings

_backend = get_storage_backend()

def job_dir(job_id: str) -> Path:
    p = _backend.job_dir(job_id)
    return Path(p) if isinstance(p, str) else p

def save_upload(job_id: str, file) -> Path:
    key = _backend.save_file(job_id, f"input_{file.filename}", file.file)
    return Path(key)

def save_uploads(job_id: str, files) -> list[Path]:
    tuples = [(f.filename, f.file) for f in files]
    keys = _backend.save_files(job_id, tuples)
    return [Path(k) for k in keys]

def make_output_path(job_id: str, ext: str, name: str = "output") -> Path:
    if settings.storage_backend == 's3':
        # just return file name; backend uses job prefix internally
        return Path(f"{name}.{ext.lstrip('.')}")
    return Path(job_dir(job_id) / f"{name}.{ext.lstrip('.')}")

def presign_download(path: Path) -> str:
    key = str(path)
    fname = Path(key).name
    return _backend.presign_download(key, force_download_name=fname)

def package_single_or_zip(job_id: str, files: list[Path], zip_name: str = "output") -> Path:
    if not files:
        raise RuntimeError("No output files produced")
    if len(files) == 1:
        return files[0]
    if settings.storage_backend == 's3':
        import io
        from .storage_backend import get_storage_backend
        be = get_storage_backend()
        key = f"jobs/{job_id}/{zip_name}.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                z.write(str(p), arcname=Path(str(p)).name)
        buf.seek(0)
        be.client.upload_fileobj(buf, be.bucket, key)  # type: ignore
        return Path(key)
    else:
        jd = job_dir(job_id)
        zip_path = jd / f"{zip_name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(f, arcname=Path(f).name)
        return zip_path
