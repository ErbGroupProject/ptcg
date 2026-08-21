from django.urls import path
from . import views

app_name = "decks"

urlpatterns = [
    path(
        "add/<int:card_id>/",
        views.add_card,
        name="add_card",
    ),
    path(
        "modify-cards/",
        views.modify_cards,
        name="modify_cards",
    ),
    path(
        "select/<int:deck_id>/",
        views.select_deck,
        name="select_deck",
    ),
    path(
        "create/",
        views.create_deck,
        name="create_deck",
    ),
    path(
        "rename/<int:deck_id>/",
        views.rename_deck,
        name="rename_deck",
    ),
    path(
        "remove-deck/<int:deck_id>/",
        views.remove_deck,
        name="remove_deck",
    ),
]