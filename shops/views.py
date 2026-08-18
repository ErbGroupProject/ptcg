from django.shortcuts import render
# Create your views here.


def shop(request):
    return render(request, "shops/shop.html")

def search_shops(request):
    return render(request, "shops/search_shops.html")

