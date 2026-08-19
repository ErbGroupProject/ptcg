from django.db import models

class Shoplist(models.Model):
    shopname = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    #district = models.CharField(max_length=50, choices=district_choices.items(),default="")
    website = models.TextField(blank=True)
    monday = models.CharField(max_length=20,blank=True)
    tuesday = models.CharField(max_length=20,blank=True)
    wednesday = models.CharField(max_length=20,blank=True)
    thursday = models.CharField(max_length=20,blank=True)
    friday = models.CharField(max_length=20,blank=True)
    saturday = models.CharField(max_length=20,blank=True)
    sunday = models.CharField(max_length=20,blank=True)
    card_identification = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    shop_logo = models.ImageField(upload_to='photos/%Y/%m/%d/',blank=True,null=True)

    def __str__(self):
<<<<<<< HEAD
        return f"{self.shopname} - {self.address}"
=======
        return self.shopname
>>>>>>> ki2
