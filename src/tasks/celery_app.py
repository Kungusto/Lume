from celery import Celery
from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tasks",
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    include=["src.tasks.tasks"],
)


celery_app.conf.beat_schedule = {
    "auto_statement": {"task": "auto_statement", "schedule": 300}
}
