from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    env: str = Field(default="dev")
    secret_key: str = Field(default="changeme")
    storage_dir: Path = Field(default=Path("/data/storage"))
    expiry_hours: int = Field(default=24)

    # Storage backend: "local" | "s3"
    storage_backend: str = Field(default="local")

    # S3/MinIO settings (used when storage_backend == "s3")
    s3_endpoint_url: str | None = None     # e.g., http://minio:9000 or https://s3.amazonaws.com
    s3_region: str | None = None
    s3_bucket: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_force_path_style: bool = True       # True for MinIO; False for AWS S3 virtual-hosted style

    redis_url: str = Field(default="redis://redis:6379/0")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
