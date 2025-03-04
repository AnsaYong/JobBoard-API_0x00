from django.contrib import admin
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ["job", "job_seeker", "status", "applied_at", "updated_at"]
    list_filter = ["status", "applied_at"]
    search_fields = ["job__title", "job_seeker__username"]


@admin.register(JobApplicationStatus)
class JobApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ["status_code", "description"]


@admin.register(JobApplicationStatusHistory)
class JobApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["job_application", "status", "changed_by", "changed_at"]
    list_filter = ["status", "changed_at"]
    search_fields = ["job_application__job__title", "changed_by__username"]
