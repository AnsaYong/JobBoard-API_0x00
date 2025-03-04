from rest_framework import serializers
from .models import JobApplication, JobApplicationStatus, JobApplicationStatusHistory


class JobApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplicationStatus
        fields = ["id", "status_code", "description"]


class JobApplicationSerializer(serializers.ModelSerializer):
    job = serializers.StringRelatedField()
    job_seeker = serializers.StringRelatedField()
    status = JobApplicationStatusSerializer()

    class Meta:
        model = JobApplication
        fields = [
            "job_application_id",
            "job",
            "job_seeker",
            "resume_url",
            "cover_letter_url",
            "status",
            "applied_at",
            "updated_at",
        ]


class JobApplicationStatusHistorySerializer(serializers.ModelSerializer):
    status = JobApplicationStatusSerializer()
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = JobApplicationStatusHistory
        fields = ["job_application", "status", "changed_at", "changed_by"]
