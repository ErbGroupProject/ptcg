from django.shortcuts import render
from banners.models import BannersItem


def index(request):
    """首頁：輪播圖（Banner）"""
    banners = BannersItem.objects.all()
    return render(request, "pages/index.html", {
        "banners_list": banners,
    })


def about(request):
    return render(request, "pages/about.html")


def news(request):
    return render(request, "pages/news.html")

def tournament(request):
    return render(request, "pages/tournament.html")

def upcoming(request):
    return render(request, "pages/tournament.html")