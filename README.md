# Enterprise Regulatory Ingestion Platform

Production-ready Django + Celery system for AI-driven regulatory document ingestion, translation, summarization, and auditability.

## Core Capabilities

- Submit regulatory URLs through a secure web UI.
- Scrape static and JavaScript-rendered pages using Playwright.
- Clean extracted content and persist raw HTML artifact references in S3-compatible storage.
- Translate non-English text through pluggable translation service interfaces.
- Summarize text through pluggable LLM summarization interfaces.
- Track every stage via audit events and structured JSON logs.
- Run asynchronous workflow with retries, backoff, and failure propagation via Celery.

## Architecture (Layered)

```text
ingestion/
  presentation/   # Django views, forms, routes
  application/    # Orchestration services, use cases, metrics
  domain/         # Entities/models and business rules
  infrastructure/ # Scraper, storage adapters, AI/translation providers, logging
```

### Workflow Sequence

1. `submit_job` task receives `job_id`.
2. Celery chain invokes:
   - `scrape_task`
   - `translate_task`
   - `summarize_task`
   - `complete_job`
3. Failures mark the job as failed and preserve the error message.
4. Retries use exponential backoff and jitter.

## Data Model

- **Job**: URL, status, timestamps, error messages.
- **ScrapedContent**: raw HTML S3 reference, cleaned text, detected language.
- **TranslationResult**: translated text, engine metadata, timestamp.
- **SummaryResult**: summary + model metadata (prompt version, temperature, token usage).
- **JobAuditEvent**: immutable stage-level audit trail.

## Observability

- JSON log formatting in `ingestion.infrastructure.logging.JsonFormatter`.
- Job stage transitions logged with `job_id` correlation metadata.
- Celery signal hooks emit task lifecycle telemetry.
- Processing durations are captured per workflow stage.

## Deployment Targets

Designed for AWS-compatible deployment:

- **Django** in ECS/Fargate or EC2.
- **PostgreSQL** in RDS.
- **Redis** in ElastiCache.
- **S3-compatible object storage** for raw HTML artifacts.

No proprietary workflow engines are required.

## Local Run (Docker Compose)

```bash
docker compose up --build
```

App endpoints:

- Dashboard: `http://localhost:8000/`
- Submit URL: `http://localhost:8000/jobs/submit/`
- Django admin: `http://localhost:8000/admin/`

## Environment Variables

All configuration is externalized in environment variables (`.env.example`):

- Django secrets and host config
- Postgres credentials/host
- Redis broker URL
- S3 credentials and endpoint
- Logging level and Celery task limits

## Production Hardening Notes

- Replace dummy translation/summarization providers with vendor-backed adapters.
- Add IAM-based auth for S3 access in cloud environments.
- Front with ALB + HTTPS and private networking.
- Add autoscaling for web and worker containers.
- Enable periodic security scans and image pinning.
