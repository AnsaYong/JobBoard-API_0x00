# Generated by Django 5.0.12 on 2025-03-11 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("job_listings", "0004_remove_location_job_listing_city_cd66de_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobposting",
            name="company",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
