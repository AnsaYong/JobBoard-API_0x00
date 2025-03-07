# Generated by Django 5.0.12 on 2025-03-07 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("job_applications", "0008_alter_jobapplicationstatushistory_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="jobapplicationstatus",
            options={
                "ordering": ["job_status_code"],
                "verbose_name_plural": "Job Application Statuses",
            },
        ),
        migrations.RenameField(
            model_name="jobapplicationstatus",
            old_name="status_code",
            new_name="job_status_code",
        ),
    ]
