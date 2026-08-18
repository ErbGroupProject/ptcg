from django.db import models
from accounts.models import Profile
from django.utils import timezone

# from shops.models import Shoplist   # 等 Shoplist 建好再開


class Tradelist(models.Model):
    user_name = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
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
    condition = models.CharField(max_length=50)
    identification_score = models.FloatField(blank=True, null=True)
    series_name = models.CharField(max_length=50, blank=True)
    series_number = models.CharField(max_length=50, blank=True)
    descriptions = models.TextField(blank=True)
    deal_place = models.CharField(max_length=200, blank=True)
    # deal_shop = models.ManyToManyField(Shoplist, blank=True)  # Shoplist 還沒建好，先註解
    is_sold = models.BooleanField(default=False, verbose_name="已下架/已售出")
    list_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        local_time = timezone.localtime(self.list_date)
        time_str = local_time.strftime('%Y-%m-%d %H:%M')
        return f"{self.sell_item_name} (release at {time_str})"
