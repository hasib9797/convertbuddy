from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import health, jobs
from .config import settings

app = FastAPI(title="Convert Buddy API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Expose generated files
app.mount("/files", StaticFiles(directory=str(settings.storage_dir), html=False), name="files")
