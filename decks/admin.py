from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from cards.models import Card
from .models import Deck, DeckCard


class DeckCardAdminForm(forms.ModelForm):

    class Meta:
        model = DeckCard
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sort Deck dropdown by ID
        self.fields["deck"].queryset = Deck.objects.order_by("id")

        # Sort Card dropdown by ID
        self.fields["card"].queryset = Card.objects.order_by("id")

    def clean(self):
        cleaned_data = super().clean()

        deck = cleaned_data.get("deck")
        card = cleaned_data.get("card")
        quantity = cleaned_data.get("quantity")

        if not deck or not card or not quantity:
            return cleaned_data

        # When creating a new DeckCard, check whether
        # this deck already contains this card.
        if not self.instance.pk:
            existing = DeckCard.objects.filter(
                deck=deck,
                card=card,
            ).first()

            if existing:
                new_quantity = existing.quantity + quantity

                if new_quantity > 4:
                    raise ValidationError(
                        f"This deck already has {existing.quantity} "
                        f"copies of {card.title}. "
                        f"You cannot add {quantity} more because "
                        f"the maximum is 4."
                    )

        return cleaned_data

    def validate_unique(self):
        # When adding a new DeckCard, we intentionally allow the
        # existing Deck + Card combination because save_model()
        # will merge it into the existing DeckCard.
        if not self.instance.pk:
            return

        super().validate_unique()


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "card_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("id",)

    def card_count(self, obj):
        return sum(
            deck_card.quantity
            for deck_card in obj.deck_cards.all()
        )

    card_count.short_description = "Cards"


@admin.register(DeckCard)
class DeckCardAdmin(admin.ModelAdmin):
    form = DeckCardAdminForm

    list_display = (
        "id",
        "deck",
        "user",
        "card",
        "quantity",
    )

    list_filter = (
        "quantity",
    )

    search_fields = (
        "deck__name",
        "deck__user__username",
        "card__title",
    )

    list_select_related = (
        "deck",
        "deck__user",
        "card",
    )

    ordering = ("id",)

    def user(self, obj):
        return obj.deck.user.username

    user.short_description = "User"

    def save_model(self, request, obj, form, change):
        if not change:
            existing = DeckCard.objects.filter(
                deck=obj.deck,
                card=obj.card,
            ).first()

            if existing:
                existing.quantity += obj.quantity
                existing.save(update_fields=["quantity"])

                obj.pk = existing.pk
                obj.quantity = existing.quantity

                return

        super().save_model(request, obj, form, change)