from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import JobPosting
from .serializers import JobPostingSerializer
from permissions import IsJobseeker, IsEmployer, IsJobBoardAdmin


class JobPostingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing job postings.
    """

    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsJobseeker]
        else:
            permission_classes = [IsEmployer]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        This view should return a list of all the job postings
        for the currently authenticated user.
        """
        # Complex SQL to retrieve job postings
        pass

    def perform_create(self, serializer):
        serializer.save(
            employer=self.request.user
        )  # Automatically assign the logged-in user as the employer
