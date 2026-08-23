from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("start/<int:listing_id>/", views.start_chat_from_listing, name="start"),
    path("chat/<int:chat_id>/", views.chat_detail, name="chat_detail"),
    path("spam/<int:chat_id>/", views.mark_as_spam, name="mark_as_spam"),
    path("unspam/<int:chat_id>/", views.unmark_spam, name="unmark_spam"),
    path("confirm/<int:chat_id>/", views.confirm_trade, name="confirm_trade"),

]
