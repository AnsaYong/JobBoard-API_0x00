from rest_framework import serializers
from django.contrib.auth import get_user_model
from job_listings.models import JobPosting
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory

User = get_user_model()


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplicationStatus
        fields = ["status_id", "status_code", "description"]


class JobApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(read_only=True)
    job_seeker = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.PrimaryKeyRelatedField(
        queryset=JobApplicationStatus.objects.all(), required=False
    )

    class Meta:
        model = JobApplication
        fields = [
            "application_id",
            "job",
            "job_seeker",
            "resume_url",
            "cover_letter_url",
            "status",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = ["application_id", "applied_at", "updated_at"]


class JobApplicationStatusHistorySerializer(serializers.ModelSerializer):
    status = JobApplicationStatusSerializer()
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = JobApplicationStatusHistory
        fields = [
            "status_hist_id",
            "job_application",
            "status",
            "changed_at",
            "changed_by",
        ]
