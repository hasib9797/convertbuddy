from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Protocol, runtime_checkable
import uuid
import mimetypes
import os

from ..config import settings

try:
    import boto3
    from botocore.config import Config as BotoConfig
except Exception:
    boto3 = None

from typing import Any

@runtime_checkable
class StorageBackend(Protocol):
    def job_dir(self, job_id: str) -> str: ...
    def save_file(self, job_id: str, filename: str, data_stream) -> str: ...
    def save_files(self, job_id: str, file_tuples: Iterable[tuple[str, Any]]) -> list[str]: ...
    def path_for(self, job_id: str, filename: str) -> str: ...
    def presign_download(self, key: str, force_download_name: str | None = None, expires_in: int = 3600) -> str: ...
    def delete_older_than(self, before: datetime) -> int: ...

# -------- Local filesystem backend --------

class LocalBackend(StorageBackend):
    base: Path
    def __init__(self, base: Path):
        self.base = Path(base)

    def job_dir(self, job_id: str) -> str:
        p = self.base / job_id
        p.mkdir(parents=True, exist_ok=True)
        return str(p)

    def save_file(self, job_id: str, filename: str, data_stream) -> str:
        safe = filename.replace('/', '_').replace('..', '.')
        p = Path(self.job_dir(job_id)) / safe
        with open(p, 'wb') as f:
            import shutil
            shutil.copyfileobj(data_stream, f)
        return str(p)

    def save_files(self, job_id: str, file_tuples: Iterable[tuple[str, Any]]) -> list[str]:
        out = []
        idx = 1
        for name, stream in file_tuples:
            safe = f"{idx:03d}_" + name.replace('/', '_').replace('..', '.')
            p = Path(self.job_dir(job_id)) / safe
            with open(p, 'wb') as f:
                import shutil
                shutil.copyfileobj(stream, f)
            out.append(str(p))
            idx += 1
        return out

    def path_for(self, job_id: str, filename: str) -> str:
        return str(Path(self.job_dir(job_id)) / filename)

    def presign_download(self, key: str, force_download_name: str | None = None, expires_in: int = 3600) -> str:
        # For local, return API proxy path under /files/
        rel = str(Path(key).absolute()).replace(str(self.base.absolute()) + os.sep, '').replace('\\', '/')
        return f"/files/{rel}"

    def delete_older_than(self, before: datetime) -> int:
        count = 0
        base = self.base
        if not base.exists():
            return 0
        for job_dir in base.iterdir():
            try:
                if not job_dir.is_dir():
                    continue
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime, tz=timezone.utc)
                if mtime < before:
                    import shutil
                    shutil.rmtree(job_dir, ignore_errors=True)
                    count += 1
            except Exception:
                pass
        return count

# -------- S3/MinIO backend --------

class S3Backend(StorageBackend):
    def __init__(self, bucket: str, endpoint_url: str | None, region: str | None, access_key: str, secret_key: str, force_path_style: bool = True):
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3 backend")
        cfg = BotoConfig(s3={"addressing_style": "path" if force_path_style else "virtual"})
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=cfg,
        )
        self.bucket = bucket

    def _job_prefix(self, job_id: str) -> str:
        return f"jobs/{job_id}/"

    def job_dir(self, job_id: str) -> str:
        # S3: logical prefix; return prefix string
        return self._job_prefix(job_id)

    def save_file(self, job_id: str, filename: str, data_stream) -> str:
        key = self._job_prefix(job_id) + filename
        self.client.upload_fileobj(data_stream, self.bucket, key)
        return key

    def save_files(self, job_id: str, file_tuples: Iterable[tuple[str, Any]]) -> list[str]:
        out = []
        idx = 1
        for name, stream in file_tuples:
            safe = f"{idx:03d}_" + name
            key = self._job_prefix(job_id) + safe
            self.client.upload_fileobj(stream, self.bucket, key)
            out.append(key)
            idx += 1
        return out

    def path_for(self, job_id: str, filename: str) -> str:
        return self._job_prefix(job_id) + filename

    def presign_download(self, key: str, force_download_name: str | None = None, expires_in: int = 3600) -> str:
        params = {"Bucket": self.bucket, "Key": key}
        # Force download
        if force_download_name:
            params["ResponseContentDisposition"] = f"attachment; filename={force_download_name}"
        else:
            import os
            params["ResponseContentDisposition"] = f"attachment; filename={os.path.basename(key)}"
        # content-type hint
        ctype, _ = mimetypes.guess_type(key)
        if ctype:
            params["ResponseContentType"] = ctype
        url = self.client.generate_presigned_url('getObject', Params=params, ExpiresIn=expires_in)
        return url

    def delete_older_than(self, before: datetime) -> int:
        paginator = self.client.get_paginator('list_objects_v2')
        deleted = 0
        for page in paginator.paginate(Bucket=self.bucket, Prefix="jobs/"):
            for obj in page.get('Contents', []) or []:
                last = obj.get('LastModified')
                if last:
                    last = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
                    if last < before:
                        self.client.delete_object(Bucket=self.bucket, Key=obj['Key'])
                        deleted += 1
        return deleted

def get_storage_backend() -> StorageBackend:
    if settings.storage_backend.lower() == 'local':
        return LocalBackend(settings.storage_dir)
    elif settings.storage_backend.lower() == 's3':
        if not all([settings.s3_bucket, settings.s3_access_key, settings.s3_secret_key]):
            raise RuntimeError("Missing S3 settings: s3_bucket, s3_access_key, s3_secret_key are required")
        return S3Backend(
            bucket=settings.s3_bucket,
            endpoint_url=settings.s3_endpoint_url,
            region=settings.s3_region,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            force_path_style=settings.s3_force_path_style,
        )
    else:
        raise RuntimeError(f"Unknown storage backend: {settings.storage_backend}")
