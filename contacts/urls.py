from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("start/<int:listing_id>/", views.start_chat_from_listing, name="start"),
    path("chat/<int:chat_id>/", views.chat_detail, name="chat_detail"),
]
