from django.db import models

# Create your models here.
from django.db import models
from listings.choices import position_choices
class Staff(models.Model):
    name = models.CharField(max_length=200)
    portrait = models.ImageField(upload_to='photos/%Y/%m/%d/')  
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    position = models.CharField(max_length=100, choices=position_choices.items(),default='')
    hire_date = models.DateTimeField(auto_now_add=True)
    is_promo = models.BooleanField(default=False)   
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name