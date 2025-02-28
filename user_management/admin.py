from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "role",
        "created_at",
        "updated_at",
    )
    list_filter = ("role",)
    search_fields = ("first_name", "last_name", "email")
    ordering = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("role",)}),
        ("Important Dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
