from datetime import datetime, timedelta, timezone
from .celery_app import celery
from ..config import settings
from ..services.storage_backend import get_storage_backend

@celery.task
def cleanup_expired():
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=settings.expiry_hours)
    be = get_storage_backend()
    deleted = be.delete_older_than(cutoff)
    return {"deleted": deleted, "before": cutoff.isoformat()}
