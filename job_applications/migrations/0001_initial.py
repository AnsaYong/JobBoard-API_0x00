# Generated by Django 5.0.12 on 2025-03-06 09:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                (
                    "job_application_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("resume_url", models.TextField()),
                ("cover_letter_url", models.TextField()),
                ("applied_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Job Applications",
            },
        ),
        migrations.CreateModel(
            name="JobApplicationStatus",
            fields=[
                (
                    "status_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("status_code", models.CharField(max_length=50, unique=True)),
                ("description", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Job Application Statuses",
            },
        ),
        migrations.CreateModel(
            name="JobApplicationStatusHistory",
            fields=[
                (
                    "status_hist_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Job Application Status History",
            },
        ),
    ]
