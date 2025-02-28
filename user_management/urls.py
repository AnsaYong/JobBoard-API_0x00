from django.urls import path
from .views import UserView, RegisterView

urlpatterns = [
    # path("users/", UserView.as_view(), name="users"),
    path("auth/register/", RegisterView.as_view(), name="register"),
]
