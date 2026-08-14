from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]