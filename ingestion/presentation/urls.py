from django.urls import path

from ingestion.presentation.views import DashboardView, JobDetailView, JobSubmitView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("jobs/submit/", JobSubmitView.as_view(), name="submit_job"),
    path("jobs/<int:job_id>/", JobDetailView.as_view(), name="job_detail"),
]
