from django.db import models
from .choices import district_choices
from geopy.geocoders import ArcGIS

class Shoplist(models.Model):
    shopname = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    district = models.CharField(max_length=50, choices=district_choices.items(),default="")
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
    latitude = models.FloatField(null=True, blank=True, verbose_name='緯度')
    longitude = models.FloatField(null=True, blank=True, verbose_name='經度')

    def save(self, *args, **kwargs):
        if self.address:
            try:
                geolocator = ArcGIS()
                location = geolocator.geocode(query=self.address)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
                    print(f"✅ 地圖自動匹配成功！座標為: {location.latitude}, {location.longitude}")
                else:
                    print("⚠️ 警告：Google/OSM 找不到這個地址，請嘗試精簡地址字串！")
            except Exception as e:
                print(f"❌ 地圖自動匹配失敗！錯誤原因為: {e}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.shopname