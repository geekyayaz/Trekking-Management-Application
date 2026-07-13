import os

from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "trekking_app",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["controllers.tasks"],
)

celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    result_expires=60 * 60 * 24,
    beat_schedule={
        "daily-trek-reminders": {
            "task": "controllers.tasks.send_daily_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
        "monthly-activity-report": {
            "task": "controllers.tasks.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=6, minute=0),
        },
    },
)


def init_celery(app):
    """
    Call this once from app.py, after creating the Flask app, e.g.:

        from controllers.celery_app import init_celery
        celery = init_celery(app)

    This makes every Celery task run inside app.app_context(), so tasks can
    freely use `db.session`, query models, etc. -- exactly like a request handler.
    """

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery