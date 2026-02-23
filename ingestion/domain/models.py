from django.db import models
from django.utils import timezone


class JobStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    FAILED = "failed", "Failed"
    COMPLETED = "completed", "Completed"


class Job(models.Model):
    url = models.URLField(max_length=2048)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PENDING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"], name="idx_job_status_created"),
        ]

    def mark_completed(self) -> None:
        self.status = JobStatus.COMPLETED
        self.completed_at = timezone.now()
        self.error_message = ""
        self.save(update_fields=["status", "completed_at", "error_message"])

    def mark_failed(self, error_message: str) -> None:
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "error_message", "completed_at"])


class ScrapedContent(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="scraped_content")
    raw_html = models.CharField(max_length=1024, help_text="S3 object reference")
    cleaned_text = models.TextField()
    detected_language = models.CharField(max_length=32, default="unknown")


class TranslationResult(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="translations")
    translated_text = models.TextField()
    translation_engine = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)


class SummaryResult(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="summaries")
    summary_text = models.TextField()
    model_name = models.CharField(max_length=128)
    prompt_version = models.CharField(max_length=64)
    temperature = models.FloatField(default=0.2)
    token_usage = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)


class JobAuditEvent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="audit_events")
    stage = models.CharField(max_length=64)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "stage", "created_at"], name="idx_job_audit_stage")]
