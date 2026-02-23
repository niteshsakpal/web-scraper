import logging
import time

from ingestion.domain.models import Job, JobStatus, ScrapedContent, SummaryResult, TranslationResult
from ingestion.infrastructure.scraper import PlaywrightScraperService
from ingestion.infrastructure.storage import S3StorageService
from ingestion.infrastructure.summarization import DummySummarizationService
from ingestion.infrastructure.translation import DummyTranslationService

logger = logging.getLogger(__name__)


class RegulatoryPipelineService:
    def __init__(self) -> None:
        self.scraper = PlaywrightScraperService()
        self.storage = S3StorageService()
        self.translator = DummyTranslationService()
        self.summarizer = DummySummarizationService()

    def scrape(self, job_id: int) -> int:
        job = Job.objects.get(id=job_id)
        job.status = JobStatus.RUNNING
        job.save(update_fields=["status"])
        start = time.monotonic()

        scraped = self.scraper.scrape_url(job.url)
        html_ref = self.storage.upload_html(scraped.raw_html, job_id=job.id)

        ScrapedContent.objects.update_or_create(
            job=job,
            defaults={
                "raw_html": html_ref,
                "cleaned_text": scraped.cleaned_text,
                "detected_language": scraped.detected_language,
            },
        )
        logger.info("pipeline.scrape.completed", extra={"job_id": job_id, "duration_seconds": round(time.monotonic() - start, 2)})
        return job_id

    def translate(self, job_id: int) -> int:
        scraped = ScrapedContent.objects.select_related("job").get(job_id=job_id)
        start = time.monotonic()
        translated = self.translator.translate(scraped.cleaned_text, scraped.detected_language)
        TranslationResult.objects.create(
            job=scraped.job,
            translated_text=translated.translated_text,
            translation_engine=translated.engine,
        )
        logger.info("pipeline.translate.completed", extra={"job_id": job_id, "duration_seconds": round(time.monotonic() - start, 2)})
        return job_id

    def summarize(self, job_id: int) -> int:
        job = Job.objects.get(id=job_id)
        latest_translation = job.translations.order_by("-timestamp").first()
        source_text = latest_translation.translated_text if latest_translation else job.scraped_content.cleaned_text
        start = time.monotonic()
        summary = self.summarizer.summarize(source_text)
        SummaryResult.objects.create(
            job=job,
            summary_text=summary.summary_text,
            model_name=summary.model_name,
            prompt_version=summary.prompt_version,
            temperature=summary.temperature,
            token_usage=summary.token_usage,
        )
        logger.info("pipeline.summarize.completed", extra={"job_id": job_id, "duration_seconds": round(time.monotonic() - start, 2)})
        return job_id

    def complete(self, job_id: int) -> int:
        job = Job.objects.get(id=job_id)
        job.mark_completed()
        logger.info("pipeline.complete", extra={"job_id": job_id})
        return job_id
