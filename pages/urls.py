from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("news/", views.news, name="news"),
    path("tournament/", views.tournament, name="tournament"),
    path("upcoming/", views.upcoming, name="upcoming"),
]

