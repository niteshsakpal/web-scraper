from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from ingestion.application.job_service import JobApplicationService
from ingestion.domain.models import Job
from ingestion.presentation.forms import JobSubmitForm
from ingestion.tasks import submit_job


class DashboardView(View):
    template_name = "ingestion/dashboard.html"

    def get(self, request):
        service = JobApplicationService()
        context = {
            "metrics": service.dashboard_metrics(),
            "recent_jobs": Job.objects.order_by("-created_at")[:10],
        }
        return render(request, self.template_name, context)


class JobSubmitView(View):
    template_name = "ingestion/submit_job.html"

    def get(self, request):
        return render(request, self.template_name, {"form": JobSubmitForm()})

    def post(self, request):
        form = JobSubmitForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        service = JobApplicationService()
        job = service.submit(form.cleaned_data["url"])
        submit_job.delay(job.id)
        messages.success(request, f"Job #{job.id} submitted successfully")
        return redirect("job_detail", job_id=job.id)


class JobDetailView(View):
    template_name = "ingestion/job_detail.html"

    def get(self, request, job_id: int):
        job = get_object_or_404(Job, id=job_id)
        context = {
            "job": job,
            "scraped": getattr(job, "scraped_content", None),
            "translation": job.translations.order_by("-timestamp").first(),
            "summary": job.summaries.order_by("-timestamp").first(),
            "audit_events": job.audit_events.order_by("-created_at")[:20],
        }
        return render(request, self.template_name, context)
