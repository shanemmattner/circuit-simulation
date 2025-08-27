"""
Celery application configuration for background job processing.
"""

import os
from celery import Celery

# Redis URL configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "circuit_simulation",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.api.workers.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=86400,  # Results expire after 24 hours
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
)

# Task routing
celery_app.conf.task_routes = {
    "src.api.workers.tasks.run_simulation": {"queue": "simulations"},
}

if __name__ == "__main__":
    celery_app.start()