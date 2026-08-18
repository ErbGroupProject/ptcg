from django.db import models
from .choices import category_choices, energy_choices, stage_choices, rarity_choices, generation_choices, modifier_choices


# class Card_Listing(models.Model):
#     category = models.CharField(max_length=50, choices=category_choices.items(),default='') #寵，#SUPPORTER,ITEM,STADIUM,POKEMON TOOL，能量
    
#     photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
#     stage = models.CharField(max_length=50, choices=stage_choices.items(),default='') #進化階段
#     title = models.CharField(max_length=50) #名稱
#     energy_type = models.CharField(max_length=50, choices=energy_choices.items(),default='')  #能量
#     hp = models.IntegerField() #血
#     rarity = models.CharField(max_length=20, choices=rarity_choices.items(),default='') #稀有度
    
#     # type = models.CharField(max_length=50) #eg:fire
#     # attribute = models.CharField(max_length=50) #屬性
#     attack = models.CharField(max_length=200, default="")
#     special_ability = models.CharField(max_length=200, default="") #血繼限界
    
#     weakness = models.CharField(max_length=50)  #弱點
#     resistance = models.CharField(max_length=50)  #強項
#     generation = models.CharField(max_length=50, choices=generation_choices.items(),default='') #代數，第幾代
#     generation_id = models.FloatField()
    
#     transaction = models.IntegerField()

class Generation(models.Model):
    name = models.CharField(max_length=50)
    total_cards = models.PositiveIntegerField()
    def __str__(self):
        return self.name
    
class Card_Listing(models.Model):
    category = models.CharField(max_length=50, choices=category_choices.items(),default='') #寵，#SUPPORTER,ITEM,STADIUM,POKEMON TOOL，能量
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    stage = models.CharField(max_length=50, choices=stage_choices.items(),default='') #進化階段
    rarity = models.CharField(max_length=20, choices=rarity_choices.items(),default='') #稀有度
    title = models.CharField(max_length=50)
    hp = models.IntegerField()
    
    energy_type = models.CharField(max_length=50,choices=energy_choices.items(),default="")
    card_number = models.PositiveIntegerField(default=0)
    generation = models.ForeignKey(Generation,on_delete=models.PROTECT,related_name='cards')
    transaction = models.IntegerField()
    @property
    def card_number_display(self):
        return f'{self.card_number:03d}/{self.generation.total_cards:03d}'

class Ability(models.Model):
    card = models.ForeignKey(Card_Listing, on_delete=models.CASCADE, related_name='abilities')
    title = models.CharField(max_length=100)
    description = models.TextField()

class Attack(models.Model):
    card = models.ForeignKey(Card_Listing, on_delete=models.CASCADE, related_name='attacks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    damage_value = models.PositiveIntegerField(null=True, blank=True)
    damage_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='', blank=True)


class AttackEnergy(models.Model):
    attack = models.ForeignKey(Attack, on_delete=models.CASCADE, related_name='energy_costs')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    quantity = models.PositiveIntegerField(default=1)


class Weakness(models.Model):
    card = models.ForeignKey(Card_Listing, on_delete=models.CASCADE, related_name='weaknesses')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    weakness_value = models.PositiveIntegerField(null=True, blank=True)
    weakness_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='x', blank=True)


class Resistance(models.Model):
    card = models.ForeignKey(Card_Listing, on_delete=models.CASCADE, related_name='resistances')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items())
    resistance_value = models.PositiveIntegerField(null=True, blank=True)
    resistance_modifier = models.CharField(max_length=1, choices=modifier_choices.items(), default='-', blank=True)


class Retreat(models.Model):
    card = models.ForeignKey(Card_Listing, on_delete=models.CASCADE, related_name='retreats')
    energy_type = models.CharField(max_length=50, choices=energy_choices.items(), default="Colorless")
    quantity = models.PositiveIntegerField(default=0)
    
