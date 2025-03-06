from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from job_listings.urls import router as job_router
from .views import (
    JobApplicationViewSet,
    JobApplicationStatusViewSet,
    JobApplicationStatusHistoryViewSet,
)


router = DefaultRouter()
router.register(
    r"statuses", JobApplicationStatusViewSet, basename="job-application-status"
)

nested_router = NestedDefaultRouter(job_router, r"jobs", lookup="job")

# Nesting application under jobs
nested_router.register(
    r"applications", JobApplicationViewSet, basename="job-application"
)

# Nesting application status under applications
nested_router.register(
    r"applications/(?P<application_id>[^/.]+)/status",
    JobApplicationStatusViewSet,
    basename="job-application-status",
)
# Nesting application status history under applications
nested_router.register(
    r"applications/(?P<application_id>[^/.]+)/status-history",
    JobApplicationStatusHistoryViewSet,
    basename="job-application-status-history",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
]
