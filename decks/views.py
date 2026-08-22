from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect

from cards.models import Card

from . import services
from .models import Deck


@login_required
def add_card(request, card_id):
    """Add a card to a deck from the card detail page."""

    card = get_object_or_404(Card, id=card_id)

    if request.method == "POST":

        deck = get_object_or_404(
            Deck,
            id=request.POST.get("deck_id"),
            user=request.user,
        )

        try:

            services.add_card_to_deck(
                deck,
                card,
                quantity=1,
            )

            messages.success(
                request,
                f"已把「{card.title}」加入牌組「{deck.name}」",
            )

        except ValidationError as exc:

            messages.error(
                request,
                exc.messages[0] if exc.messages else str(exc),
            )

    return redirect(
        "listings:card_detail",
        card.id,
    )


@login_required
def create_deck(request):
    """Create a new deck."""

    if request.method == "POST":

        name = request.POST.get("name", "").strip()

        if not name:

            messages.error(
                request,
                "請輸入牌組名稱",
            )

        else:

            Deck.objects.create(
                user=request.user,
                name=name,
            )

            messages.success(
                request,
                f"已建立牌組「{name}」",
            )

    return redirect("listings:card_listings")


@login_required
def rename_deck(request, deck_id):
    """Rename a deck."""

    deck = get_object_or_404(
        Deck,
        id=deck_id,
        user=request.user,
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()

        if not name:

            messages.error(
                request,
                "請輸入牌組名稱",
            )

        else:

            deck.name = name
            deck.save()

            messages.success(
                request,
                f"已改名為「{name}」",
            )

    return redirect("listings:card_listings")


@login_required
def select_deck(request, deck_id):
    """Select the active deck."""

    deck = get_object_or_404(
        Deck,
        id=deck_id,
        user=request.user,
    )

    request.session["selected_deck_id"] = deck.id

    return redirect("listings:card_listings")


@login_required
def modify_cards(request):
    """Add or remove cards from a deck."""

    if request.method != "POST":
        return redirect("listings:card_listings")

    deck = get_object_or_404(
        Deck,
        id=request.POST.get("deck_id"),
        user=request.user,
    )

    action = request.POST.get("action")
    card_ids = request.POST.getlist("card_ids")

    if not card_ids:

        messages.warning(
            request,
            "Please select at least one card.",
        )

        return redirect("listings:card_listings")

    if action not in ("add", "remove"):

        messages.error(
            request,
            "Invalid action.",
        )

        return redirect("listings:card_listings")

    success_count = 0
    errors = []

    for card_id in card_ids:

        card = get_object_or_404(
            Card,
            id=card_id,
        )

        try:

            if action == "add":

                services.add_card_to_deck(
                    deck,
                    card,
                    quantity=1,
                )

            else:

                services.remove_card_from_deck(
                    deck,
                    card,
                    quantity=1,
                )

            success_count += 1

        except ValidationError as exc:

            errors.append(
                exc.messages[0]
                if exc.messages
                else str(exc)
            )

    for error in errors:

        messages.error(
            request,
            error,
        )

    if success_count:

        if action == "add":

            messages.success(
                request,
                f"{success_count} card(s) added to {deck.name}.",
            )

        else:

            messages.success(
                request,
                f"{success_count} card(s) removed from {deck.name}.",
            )

    return redirect("listings:card_listings")


@login_required
def remove_deck(request, deck_id):
    """Delete a deck."""

    deck = get_object_or_404(
        Deck,
        id=deck_id,
        user=request.user,
    )

    if request.method == "POST":

        deck_name = deck.name

        deck.delete()

        request.session.pop(
            "selected_deck_id",
            None,
        )

        messages.success(
            request,
            f"已刪除牌組「{deck_name}」",
        )

    return redirect("listings:card_listings")