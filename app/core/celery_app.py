from celery import Celery
from celery.schedules import crontab

from app.config import settings


celery_app = Celery(
    "cashback_aggregator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "deactivate-expired-coupons-daily": {
        "task": "app.core.tasks.deactivate_expired_coupons",
        "schedule": crontab(hour=0, minute=0),
    }
}

# Ensure task modules are imported and registered.
celery_app.autodiscover_tasks(["app.core"])
