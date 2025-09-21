from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict

class JobCreate(BaseModel):
    target: str = Field(..., description="e.g., 'pdf->jpg', 'mp4->mp3'")
    options: Optional[Dict] = None

class JobInfo(BaseModel):
    job_id: str
    status: Literal["queued","processing","done","error"]
    progress: int = 0
    download_url: Optional[str] = None
    error: Optional[str] = None
