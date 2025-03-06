from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndustryViewSet, LocationViewSet, SkillViewSet, JobPostingViewSet


router = DefaultRouter()
router.register(r"industries", IndustryViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"jobs", JobPostingViewSet, basename="job")

urlpatterns = [
    path("", include(router.urls)),
]
