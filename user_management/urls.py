from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView, RegisterView, LoginView, LogoutView

router = DefaultRouter()
router.register(r"users", UserView, basename="users")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
