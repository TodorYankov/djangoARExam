# products/tasks.py
from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def test_celery():
    """Тестова задача за проверка на Celery"""
    logger.info("Test task started")
    time.sleep(2)
    logger.info("Test task completed")
    return {
        "status": "success",
        "message": "Celery is working correctly!"
    }
