from celery import Celery
from ..config import settings

celery = Celery(
    "convertbuddy",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
