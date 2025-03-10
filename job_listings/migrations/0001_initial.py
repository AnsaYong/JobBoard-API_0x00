# Generated by Django 5.0.12 on 2025-03-06 09:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobPosting",
            fields=[
                (
                    "job_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(db_index=True, max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255, unique=True)),
                ("description", models.TextField()),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("part-time", "Part-time"),
                            ("full-time", "Full-time"),
                            ("contract", "Contract"),
                            ("internship", "Internship"),
                            ("remote", "Remote"),
                            ("freelance", "Freelance"),
                            ("temporary", "Temporary"),
                            ("volunteer", "Volunteer"),
                        ],
                        db_index=True,
                        max_length=50,
                    ),
                ),
                (
                    "salary_min",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "salary_max",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("currency", models.CharField(default="ZAR", max_length=10)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("expiration_date", models.DateTimeField(db_index=True)),
                ("posted_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Job Posting",
                "verbose_name_plural": "Job Postings",
                "ordering": ["expiration_date", "-posted_at"],
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "location_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("city", models.CharField(max_length=100)),
                ("postal_code", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "state_or_province",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("country", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name": "Job Location",
                "verbose_name_plural": "Job Locations",
            },
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                (
                    "skill_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Industry",
            fields=[
                (
                    "industry_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Industry",
                "verbose_name_plural": "Industries",
                "indexes": [
                    models.Index(fields=["name"], name="job_listing_name_3f9dc6_idx")
                ],
            },
        ),
    ]
