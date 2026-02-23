import logging

from celery import chain, shared_task

from ingestion.application.job_service import JobApplicationService
from ingestion.application.pipeline_service import RegulatoryPipelineService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def submit_job(self, job_id: int) -> str:
    logger.info("task.submit_job", extra={"job_id": job_id})
    workflow = chain(
        scrape_task.s(job_id),
        translate_task.s(),
        summarize_task.s(),
        complete_job.s(),
    )
    workflow.delay()
    return f"workflow_started:{job_id}"


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def scrape_task(self, job_id: int) -> int:
    pipeline = RegulatoryPipelineService()
    try:
        return pipeline.scrape(job_id)
    except Exception as exc:
        JobApplicationService().fail_job(job_id, str(exc))
        raise


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def translate_task(self, job_id: int) -> int:
    pipeline = RegulatoryPipelineService()
    try:
        return pipeline.translate(job_id)
    except Exception as exc:
        JobApplicationService().fail_job(job_id, str(exc))
        raise


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def summarize_task(self, job_id: int) -> int:
    pipeline = RegulatoryPipelineService()
    try:
        return pipeline.summarize(job_id)
    except Exception as exc:
        JobApplicationService().fail_job(job_id, str(exc))
        raise


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def complete_job(self, job_id: int) -> int:
    pipeline = RegulatoryPipelineService()
    return pipeline.complete(job_id)
