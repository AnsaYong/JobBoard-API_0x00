from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobPostingViewSet, LocationViewSet, IndustryViewSet


router = DefaultRouter()
router.register(r"", JobPostingViewSet, basename="jobs")  # api/jobs/

router.register(r"locations", LocationViewSet)  # `api/jobs/locations`
router.register(r"industries", IndustryViewSet)  # `api/jobs/industries`

urlpatterns = [
    path("", include(router.urls)),
]
