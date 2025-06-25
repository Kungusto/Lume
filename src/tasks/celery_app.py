from celery import Celery
from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tasks",
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    include=["src.tasks.tasks"],
)
