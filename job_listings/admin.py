from django.contrib import admin
from .models import JobType, Industry, Location, JobPosting


@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "state", "country")
    search_fields = ("city", "state", "country")
    ordering = ("city", "state", "country")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "job_type",
        "location",
        "industry",
        "expiration_date",
        "posted_at",
        "updated_at",
    )
    list_filter = ("job_type", "location", "industry")
    search_fields = ("title", "employer__email")
    ordering = ("posted_at", "employer")
    readonly_fields = ("posted_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "employer", "description")}),
        (
            "Job Info",
            {
                "fields": (
                    "job_type",
                    "location",
                    "industry",
                    "skills_required",
                    "salary_range",
                )
            },
        ),
        ("Important Dates", {"fields": ("expiration_date", "posted_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "title",
                    "employer",
                    "description",
                    "job_type",
                    "location",
                    "industry",
                    "skills_required",
                    "salary_range",
                    "expiration_date",
                ),
            },
        ),
    )
