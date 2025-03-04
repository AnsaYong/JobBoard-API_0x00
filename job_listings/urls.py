from django.urls import path, include

# from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import DefaultRouter
from .views import JobPostingViewSet

router = DefaultRouter()
router.register(r"", JobPostingViewSet, basename="job-posting")  # `api/jobs/`

urlpatterns = [
    path("", include(router.urls)),
]
