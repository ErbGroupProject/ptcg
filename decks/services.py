from django.core.exceptions import ValidationError
from django.db import models, transaction

from .models import DeckCard


MAX_DECK_SIZE = 60
MAX_CARD_QUANTITY = 4


def validate_deck(deck):
    """
    Check whether a deck follows the deck-building rules.

    Raises:
        ValidationError: if the deck is invalid.

    Returns:
        True if the deck is valid.
    """

    errors = []

    deck_cards = DeckCard.objects.filter(deck=deck)

    # Check total number of cards
    total_cards = (
        deck_cards.aggregate(
            total=models.Sum("quantity")
        )["total"]
        or 0
    )

    if total_cards > MAX_DECK_SIZE:
        errors.append(
            f"Deck contains {total_cards} cards. "
            f"Maximum is {MAX_DECK_SIZE}."
        )

    # Check maximum copies of each card
    cards_over_limit = deck_cards.filter(
        quantity__gt=MAX_CARD_QUANTITY
    )

    for deck_card in cards_over_limit:
        errors.append(
            f"{deck_card.card.title} has "
            f"{deck_card.quantity} copies. "
            f"Maximum is {MAX_CARD_QUANTITY}."
        )

    if errors:
        raise ValidationError(errors)

    return True


@transaction.atomic
def add_card_to_deck(deck, card, quantity=1):
    """
    Add copies of a card to a deck.

    If the card is already in the deck, increase its quantity.
    """

    if quantity < 1:
        raise ValidationError(
            "Quantity must be at least 1."
        )

    deck_card, created = DeckCard.objects.get_or_create(
        deck=deck,
        card=card,
        defaults={"quantity": 0},
    )

    new_quantity = deck_card.quantity + quantity

    # Maximum 4 copies of a card
    if new_quantity > MAX_CARD_QUANTITY:
        raise ValidationError(
            f"You cannot have more than "
            f"{MAX_CARD_QUANTITY} copies of "
            f"{card.title}."
        )

    # Calculate current deck size
    current_total = (
        DeckCard.objects
        .filter(deck=deck)
        .exclude(pk=deck_card.pk)
        .aggregate(
            total=models.Sum("quantity")
        )["total"]
        or 0
    )

    # Check maximum 60 cards
    if current_total + new_quantity > MAX_DECK_SIZE:
        raise ValidationError(
            f"A deck cannot contain more than "
            f"{MAX_DECK_SIZE} cards."
        )

    deck_card.quantity = new_quantity
    deck_card.save(update_fields=["quantity"])

    return deck_card


@transaction.atomic
def remove_card_from_deck(deck, card, quantity=1):
    """
    Remove copies of a card from a deck.

    Example:

        Charizard x4
        remove_card_from_deck(deck, charizard, 1)
        -> Charizard x3

    If removing the final copy, the DeckCard record is deleted.
    """

    if quantity < 1:
        raise ValidationError(
            "Quantity must be at least 1."
        )

    try:
        deck_card = DeckCard.objects.get(
            deck=deck,
            card=card
        )
    except DeckCard.DoesNotExist:
        raise ValidationError(
            f"{card.title} is not in this deck."
        )

    new_quantity = deck_card.quantity - quantity

    if new_quantity < 0:
        raise ValidationError(
            f"You only have {deck_card.quantity} "
            f"copies of {card.title} in this deck."
        )

    if new_quantity == 0:
        deck_card.delete()
    else:
        deck_card.quantity = new_quantity
        deck_card.save(update_fields=["quantity"])

    return True


@transaction.atomic
def change_card_quantity(deck, card, quantity):
    """
    Set a card to an exact quantity.

    Example:

        Charizard x2
        change_card_quantity(deck, charizard, 4)
        -> Charizard x4
    """

    if quantity < 0:
        raise ValidationError(
            "Quantity cannot be negative."
        )

    if quantity > MAX_CARD_QUANTITY:
        raise ValidationError(
            f"You cannot have more than "
            f"{MAX_CARD_QUANTITY} copies of "
            f"{card.title}."
        )

    try:
        deck_card = DeckCard.objects.get(
            deck=deck,
            card=card
        )
    except DeckCard.DoesNotExist:

        # If quantity is 0, there's nothing to do
        if quantity == 0:
            return None

        # Otherwise create the relationship
        deck_card = DeckCard(
            deck=deck,
            card=card,
            quantity=quantity
        )

    # Calculate deck size excluding this card
    current_total = (
        DeckCard.objects
        .filter(deck=deck)
        .exclude(pk=deck_card.pk)
        .aggregate(
            total=models.Sum("quantity")
        )["total"]
        or 0
    )

    if current_total + quantity > MAX_DECK_SIZE:
        raise ValidationError(
            f"A deck cannot contain more than "
            f"{MAX_DECK_SIZE} cards."
        )

    # Quantity 0 means remove the card
    if quantity == 0:
        if deck_card.pk:
            deck_card.delete()

        return None

    deck_card.quantity = quantity
    deck_card.save()

    return deck_card