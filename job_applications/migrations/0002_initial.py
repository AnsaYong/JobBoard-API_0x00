# Generated by Django 5.0.12 on 2025-03-06 09:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("job_applications", "0001_initial"),
        ("job_listings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="job",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="applications",
                to="job_listings.jobposting",
            ),
        ),
    ]
