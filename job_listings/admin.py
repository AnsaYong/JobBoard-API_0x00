from django.contrib import admin
from .models import Industry, Location, Skill, JobPosting


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "created_at")
    ordering = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "postal_code", "state_or_province", "country")
    search_fields = ("city", "country")
    ordering = ("city", "country")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        "employer",
        "title",
        "slug",
        "description",
        "job_type",
        "location",
        "industry",
        # "skills_required", (many-to-many field - moved to `filter_horizontal` below)
        "salary_min",
        "salary_max",
        "currency",
        "is_active",
        "expiration_date",
        "posted_at",
        "updated_at",
    )
    filter_horizontal = ("skills_required",)
    list_filter = ("job_type", "location", "industry")
    search_fields = ("title", "employer__email")
    ordering = ("posted_at", "employer")
    readonly_fields = ("posted_at", "updated_at")
    fieldsets = (
        (
            "Job Posting",
            {
                "fields": (
                    "employer",
                    "title",
                    "description",
                    "job_type",
                    "location",
                    "industry",
                    "skills_required",
                    "salary_min",
                    "salary_max",
                    "currency",
                    "is_active",
                    "expiration_date",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "posted_at",
                    "updated_at",
                )
            },
        ),
    )
