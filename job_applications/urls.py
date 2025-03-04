from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from job_listings.urls import router as job_router
from .views import JobApplicationViewSet, JobApplicationStatusViewSet


router = DefaultRouter()
router.register(
    r"statuses", JobApplicationStatusViewSet, basename="job-application-status"
)  # For admin to add new statuses

# Nest application under jobs
nested_router = NestedDefaultRouter(job_router, r"", lookup="job")
nested_router.register(
    r"applications", JobApplicationViewSet, basename="job-application"
)

urlpatterns = [
    path("", include(router.urls)),  # Standalone application statuses
    path("", include(nested_router.urls)),  # Nested applications under jobs
]
