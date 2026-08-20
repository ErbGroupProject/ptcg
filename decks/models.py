from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Deck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="decks")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DeckCard(models.Model):
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="deck_cards"
    )

    card = models.ForeignKey(
        "cards.Card",
        on_delete=models.CASCADE,
        related_name="deck_cards"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["deck", "card"],
                name="unique_card_per_deck",
            ),
        ]

    def __str__(self):
        return f"{self.card.title} x{self.quantity}"
