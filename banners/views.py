from django.shortcuts import render
from .models import BannersItem

def index(request):
    # 查询所有轮播图，可以加 .all() / .filter() 做筛选
    banners = BannersItem.objects.all()
    # 把查询到的数据通过context传给html模板
    context = {
        "banners_list": banners
    }
    return render(request, "banners/index.html", context)
