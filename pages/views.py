from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from banners.models import BannersItem

def index(request):
    # 查询所有轮播图，可以加 .all() / .filter() 做筛选
    banners = BannersItem.objects.all()
    # 把查询到的数据通过context传给html模板
    context = {
        "banners_list": banners
    }
    return render(request, "pages/index.html", context)

def about(request):
    return render(request, "pages/about.html")
# # Create your views here.
def news(request):
    return render(request, "pages/news.html")
# def shops(request):
#     return render(request, "pages/shops.html")

# def index(request):
#     return render(request, "pages/index.html")

