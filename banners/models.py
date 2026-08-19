from django.db import models

class BannersItem(models.Model):
    banner_id = models.CharField(max_length=100, verbose_name="轮播标识")
    photo_banner = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name="轮播图片")
    url_link = models.CharField(max_length=100, verbose_name="跳转链接")

    def __str__(self):
        return self.banner_id
