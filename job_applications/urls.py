from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from job_listings.urls import router as job_router
from .views import (
    ApplicationStatusViewSet,
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
applications_router = NestedDefaultRouter(
    nested_router, r"applications", lookup="application"
)
applications_router.register(
    r"status", ApplicationStatusViewSet, basename="job-application-status"
)

# Nesting application status history under applications
applications_router.register(
    r"status-history",
    JobApplicationStatusHistoryViewSet,
    basename="job-application-status-history",
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
    path("", include(applications_router.urls)),
]
