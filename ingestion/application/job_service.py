import logging
from datetime import timedelta

from django.db.models import Avg, DurationField, ExpressionWrapper, F
from django.utils import timezone

from ingestion.domain.models import Job, JobAuditEvent, JobStatus

logger = logging.getLogger(__name__)


class JobApplicationService:
    def submit(self, url: str) -> Job:
        job = Job.objects.create(url=url, status=JobStatus.PENDING)
        JobAuditEvent.objects.create(job=job, stage="submit_job", detail="Job submitted")
        logger.info("job.submitted", extra={"job_id": job.id})
        return job

    def update_status(self, job_id: int, status: str, detail: str = "") -> Job:
        job = Job.objects.get(id=job_id)
        job.status = status
        if status == JobStatus.COMPLETED:
            job.completed_at = timezone.now()
        job.save(update_fields=["status", "completed_at"] if status == JobStatus.COMPLETED else ["status"])
        JobAuditEvent.objects.create(job=job, stage=status, detail=detail)
        logger.info("job.status.updated", extra={"job_id": job_id})
        return job

    def fail_job(self, job_id: int, error_message: str) -> Job:
        job = Job.objects.get(id=job_id)
        job.mark_failed(error_message)
        JobAuditEvent.objects.create(job=job, stage="failed", detail=error_message)
        logger.error("job.failed", extra={"job_id": job_id, "error": error_message})
        return job

    def dashboard_metrics(self) -> dict[str, float | int]:
        total_jobs = Job.objects.count()
        completed_jobs = Job.objects.filter(status=JobStatus.COMPLETED).count()
        failed_jobs = Job.objects.filter(status=JobStatus.FAILED).count()

        avg_expr = ExpressionWrapper(
            F("completed_at") - F("created_at"),
            output_field=DurationField(),
        )
        avg_duration_raw = (
            Job.objects.filter(completed_at__isnull=False)
            .annotate(duration=avg_expr)
            .aggregate(avg_duration=Avg("duration"))["avg_duration"]
        )
        avg_processing_time = 0.0
        if isinstance(avg_duration_raw, timedelta):
            avg_processing_time = avg_duration_raw.total_seconds()

        success_rate = round((completed_jobs / total_jobs) * 100, 2) if total_jobs else 0.0

        return {
            "total_jobs": total_jobs,
            "success_rate": success_rate,
            "avg_processing_time": round(avg_processing_time, 2),
            "failure_count": failed_jobs,
        }
