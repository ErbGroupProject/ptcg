from django.urls import path
from . import views

app_name = "tradings"

urlpatterns = [
    path("review/<int:chat_id>/", views.submit_review, name="submit_review"),
    path("record/<int:record_id>/", views.public_record, name="public_record"),
]
