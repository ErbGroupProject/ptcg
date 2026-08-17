from django.contrib import admin
from .models import Shoplist

#class Shoplist(models.Model):
#    shopname = models.CharField(max_length=200)
#    address = models.CharField(max_length=200)
#    #district = models.CharField(max_length=50, choices=district_choices.items(),default="")
#    website = models.TextField(blank=True)
#    monday = models.CharField(max_length=20)
#    tuesday = models.CharField(max_length=20)
#    wednesday = models.CharField(max_length=20)
#    thursday = models.CharField(max_length=20)
#    friday = models.CharField(max_length=20)
#    saturday = models.CharField(max_length=20)
#    sunday = models.CharField(max_length=20)
#    card_identification = models.BooleanField(default=False)
#    phone_number = models.CharField(max_length=20, blank=True)
#    shop_logo = models.ImageField(upload_to='photos/%Y/%m/%d/')

#    def __str__(self):
#        return f"{self.shopname} - {self.address}"