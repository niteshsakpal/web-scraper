from django.contrib import admin

from ingestion.domain.models import Job, JobAuditEvent, ScrapedContent, SummaryResult, TranslationResult


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("url",)


@admin.register(ScrapedContent)
class ScrapedContentAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "detected_language")


@admin.register(TranslationResult)
class TranslationResultAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "translation_engine", "timestamp")


@admin.register(SummaryResult)
class SummaryResultAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "model_name", "prompt_version", "timestamp")


@admin.register(JobAuditEvent)
class JobAuditEventAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "stage", "created_at")
