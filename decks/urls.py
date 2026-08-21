from django.urls import path

from . import views

app_name = "decks"

urlpatterns = [
    path("add/<int:card_id>/", views.add_card, name="add_card"),
    path("create/", views.create_deck, name="create_deck"),
    path("rename/<int:deck_id>/", views.rename_deck, name="rename_deck"),
]
