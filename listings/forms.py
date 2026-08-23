from django import forms
from .models import Tradelist


class ListingForm(forms.ModelForm):
    class Meta:
        model = Tradelist
        fields = [
            'sell_item_name',
            'sell_item_main_photo',
            'photo_2', 'photo_3', 'photo_4', 'photo_5',
            'photo_6', 'photo_7', 'photo_8', 'photo_9',
            'price',
            'condition',
            'identification_score',
            'series_name',
            'series_number',
            'descriptions',
            'deal_place',
        ]
