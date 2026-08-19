from django.contrib import admin
import nested_admin

from .models import (
    Card,
    Generation,
    Ability,
    Attack,
    Energy_Cost,
    Weakness,
    Resistance,
    Retreat,
)


# ============================================================
# Generation
# ============================================================

@admin.register(Generation)
class GenerationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'total_cards',
    )

    search_fields = (
        'name',
    )


# ============================================================
# Card Listing Inlines
# ============================================================

class AbilityInline(nested_admin.NestedTabularInline):
    model = Ability
    extra = 0


class Energy_CostInline(nested_admin.NestedTabularInline):
    model = Energy_Cost
    extra = 1


class AttackInline(nested_admin.NestedStackedInline):
    model = Attack
    extra = 0

    inlines = [
        Energy_CostInline,
    ]


class WeaknessInline(nested_admin.NestedTabularInline):
    model = Weakness
    extra = 0


class ResistanceInline(nested_admin.NestedTabularInline):
    model = Resistance
    extra = 0


class RetreatInline(nested_admin.NestedTabularInline):
    model = Retreat
    extra = 0


# ============================================================
# Card Listing
# ============================================================

@admin.register(Card)
class CardAdmin(nested_admin.NestedModelAdmin):

    list_display = (
        'title',
        'card_number_display',
        'generation',
        'category',
        'stage',
        'energy_type',
        'hp',
        'rarity',
        'transaction',
    )

    list_filter = (
        'category',
        'stage',
        'energy_type',
        'rarity',
        'generation',
    )

    search_fields = (
        'title',
    )

    ordering = (
        'generation',
        'card_number',
    )

    inlines = [
        AbilityInline,
        AttackInline,
        WeaknessInline,
        ResistanceInline,
        RetreatInline,
    ]

    @admin.display(
        description='Card Number',
        ordering='card_number',
    )
    def card_number_display(self, obj):
        return f'{obj.card_number:03d}/{obj.generation.total_cards:03d}'


# ============================================================
# Attack
# ============================================================

@admin.register(Attack)
class AttackAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'card',
        'damage_display',
    )

    search_fields = (
        'title',
        'card__title',
    )

    list_filter = (
        'damage_modifier',
    )

    @admin.display(description='Damage')
    def damage_display(self, obj):
        if obj.damage_value is None:
            return '-'

        modifier = obj.damage_modifier or ''
        return f'{obj.damage_value}{modifier}'


# ============================================================
# Ability
# ============================================================

@admin.register(Ability)
class AbilityAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'card',
    )

    search_fields = (
        'title',
        'card__title',
    )


# ============================================================
# Attack Energy
# ============================================================

@admin.register(Energy_Cost)
class Energy_CostAdmin(admin.ModelAdmin):

    list_display = (
        'attack',
        'card_title',
        'energy_type',
        'quantity',
    )

    list_filter = (
        'energy_type',
    )

    search_fields = (
        'attack__title',
        'attack__card__title',
    )

    @admin.display(description='Card')
    def card_title(self, obj):
        return obj.attack.card.title


# ============================================================
# Weakness
# ============================================================

@admin.register(Weakness)
class WeaknessAdmin(admin.ModelAdmin):

    list_display = (
        'card',
        'energy_type',
        'weakness_display',
    )

    list_filter = (
        'energy_type',
        'weakness_modifier',
    )

    search_fields = (
        'card__title',
    )

    @admin.display(description='Weakness')
    def weakness_display(self, obj):
        if obj.weakness_value is None:
            return '-'

        modifier = obj.weakness_modifier or ''
        return f'{obj.weakness_value}{modifier}'


# ============================================================
# Resistance
# ============================================================

@admin.register(Resistance)
class ResistanceAdmin(admin.ModelAdmin):

    list_display = (
        'card',
        'energy_type',
        'resistance_display',
    )

    list_filter = (
        'energy_type',
        'resistance_modifier',
    )

    search_fields = (
        'card__title',
    )

    @admin.display(description='Resistance')
    def resistance_display(self, obj):
        if obj.resistance_value is None:
            return '-'

        modifier = obj.resistance_modifier or ''
        return f'{modifier}{obj.resistance_value}'


# ============================================================
# Retreat
# ============================================================

@admin.register(Retreat)
class RetreatAdmin(admin.ModelAdmin):

    list_display = (
        'card',
        'energy_type',
        'quantity',
    )

    list_filter = (
        'energy_type',
    )

    search_fields = (
        'card__title',
    )