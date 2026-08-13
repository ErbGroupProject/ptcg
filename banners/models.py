from django.db import models

# Create your models here.

class Banner(models.Model):
    banner_image=models.ImageField(upload_to='photos/%Y/%m/%d/',blank=True)
    link=models.CharField(max_length=200)