# Ensure Celery app is loaded when Django starts
from app.celery import app as celery_app  # noqa: F401

__all__ = ('celery_app',)
