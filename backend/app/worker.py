import os
from celery import Celery

# Default redis url (assuming localhost for dev)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "hackathon_tracker_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # Max 1 hour
    worker_max_tasks_per_child=500
)

# Discover tasks from tasks modules
celery_app.autodiscover_tasks(["app.tasks"])

@celery_app.task
def health_check():
    return {"status": "ok", "message": "Celery worker is running"}
