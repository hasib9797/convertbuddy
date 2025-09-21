from celery import Celery
from ..config import settings

celery = Celery(
    "convertbuddy",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Periodic cleanup schedule (hourly)
celery.conf.beat_schedule = {
    "cleanup-expired-hourly": {
        "task": "backend.app.workers.cleanup.cleanup_expired",
        "schedule": 3600.0,
    }
}
