import os

from celery import Celery
from celery.signals import task_failure, task_prerun, task_postrun

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reg_ingestion.settings")

app = Celery("reg_ingestion")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@task_prerun.connect
def task_prerun_handler(*_, task_id: str, task, **__) -> None:
    task.logger.info("celery.task.started", extra={"task_id": task_id, "task_name": task.name})


@task_postrun.connect
def task_postrun_handler(*_, task_id: str, task, state: str, **__) -> None:
    task.logger.info(
        "celery.task.finished",
        extra={"task_id": task_id, "task_name": task.name, "state": state},
    )


@task_failure.connect
def task_failure_handler(*_, task_id: str, exception: Exception, sender=None, **__) -> None:
    task_name = sender.name if sender else "unknown"
    app.log.get_default_logger().error(
        "celery.task.failed",
        extra={"task_id": task_id, "task_name": task_name, "error": str(exception)},
    )
