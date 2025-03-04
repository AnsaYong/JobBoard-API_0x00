from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import JobApplicationViewSet, JobApplicationStatusViewSet
from job_listings.views import JobPostingViewSet

router = routers.DefaultRouter()
router.register(r"jobs", JobPostingViewSet, basename="job-posting")
router.register(
    r"application-statuses",
    JobApplicationStatusViewSet,
    basename="job-application-status",
)

job_router = routers.NestedDefaultRouter(router, r"jobs", lookup="job")
job_router.register(r"applications", JobApplicationViewSet, basename="job-application")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(job_router.urls)),
]
