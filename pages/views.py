from django.shortcuts import render
from django.http import HttpResponse
from banners.models import Banner
# Create your views here.

def shops(request):
    return render(request, "pages/shops.html")

def index(request):
    return render(request, "pages/index.html")

