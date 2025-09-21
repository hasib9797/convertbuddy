from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, jobs, files
from .config import settings

app = FastAPI(title="Convert Buddy API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# Custom file router that forces download (no StaticFiles mount)
app.include_router(files.router, tags=["files"])
