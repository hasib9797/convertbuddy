from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    env: str = Field(default="dev")
    secret_key: str = Field(default="changeme")
    storage_dir: Path = Field(default=Path("/data/storage"))
    expiry_hours: int = Field(default=24)
    redis_url: str = Field(default="redis://redis:6379/0")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
