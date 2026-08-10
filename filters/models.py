from django.db import models

# Create your models here.
    
# class Card_Listing(models.Model):
#     name=models.CharField(max_length=50) #名稱
#     category_choices=models.CharField(max_length=50) #寵，#SUPPORTER,ITEM,STADIUM,POKEMON TOOL，能量
#     energy_type=models.CharField(max_length=50)  #能量
#     resistance=models.CharField(max_length=50)  #強項
#     type=models.CharField(max_length=50) #eg:fire
#     weakness=models.CharField(max_length=50)  #弱點
#     generation=models.TextField() #代數，第幾代
#     generation_id=models.CharField(max_length=50)
#     attribute=models.CharField(max_length=50) #屬性
#     special_ability=models.CharField(max_length=50) #血繼限界
#     rarity=models.CharField(max_length=20) #稀有度
#     hp=models.IntegerField() #血
#     stage=models.CharField() #進化階段

#     def __str__(self):
#         return self.name