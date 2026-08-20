from django.db import models
from accounts.models import Profile
from shops.models import Shoplist
from django.utils import timezone

class Tradelist(models.Model):
    user_name = models.ForeignKey(Profile, on_delete = models.DO_NOTHING)
    sell_item_name = models.CharField(max_length=50)
    sell_item_main_photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_7 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_8 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_9 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    price = models.IntegerField(default=0)
    condition = models.CharField(max_length=50)#使用狀況:全新，9成新，輕度使用，重度使用
    identification_score = models.FloatField(blank=True)#鑑定評分
    series_name = models.CharField(max_length=50,blank=True)#系列名稱
    descriptions = models.TextField(blank=True)
    deal_place = models.CharField(max_length=200,blank=True)
    #deal_shop = models.ManyToManyField(Shoplist, blank=True)#推薦交易商店
    list_date = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        local_time = timezone.localtime(self.list_date)
        time_str = local_time.strftime('%Y-%m-%d %H:%M')
        return f"{self.title} (release at {time_str})"