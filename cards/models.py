from django.db import models
from .choices import category_choices, energy_choices, stage_choices, rarity_choices, modifier_choices

class Generation(models.Model):
    name = models.CharField(max_length=50)
    total_cards = models.PositiveIntegerField()
    def __str__(self):
        return self.name
    
class Card(models.Model):
    category = models.CharField(max_length=50, choices=category_choices.items(),default='pokemon') #寵，#SUPPORTER,ITEM,STADIUM,POKEMON TOOL，能量
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    stage = models.CharField(max_length=50, choices=stage_choices.items(),default='', blank=True) #進化階段
    rarity = models.CharField(max_length=20, choices=rarity_choices.items(),default='') #稀有度
    title = models.CharField(max_length=50)
    hp = models.IntegerField(blank=True, null=True)
    
    energy_type = models.CharField(max_length=50,choices=energy_choices.items(),default="")
    card_number = models.PositiveIntegerField()
    generation = models.ForeignKey(Generation,on_delete=models.PROTECT,related_name='cards')
    transaction = models.IntegerField()
    @property
    def card_number_display(self):
        return f'{self.card_number:03d}/{self.generation.total_cards:03d}'

class Ability(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='abilities')
    title = models.CharField(max_length=100)
    description = models.TextField()

class Attack(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='attacks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    damage_value = models.PositiveIntegerField(null=True, blank=True)
    damage_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='', blank=True)


class Energy_Cost(models.Model):
    attack = models.ForeignKey(Attack, on_delete=models.CASCADE, related_name='energy_costs')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    quantity = models.PositiveIntegerField(default=1)


class Weakness(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='weaknesses')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    weakness_value = models.PositiveIntegerField(null=True, blank=True)
    weakness_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='x', blank=True)


class Resistance(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='resistances')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    resistance_value = models.PositiveIntegerField(null=True, blank=True)
    resistance_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='-', blank=True)


class Retreat(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='retreats')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items(), default="Colorless")
    quantity = models.PositiveIntegerField(default=0)