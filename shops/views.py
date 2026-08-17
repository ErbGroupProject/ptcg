from django.shortcuts import render

def shop(request):
    return render(request, "shops/shop.html")

def search_shops(request):
    return render(request, "shops/search_shops.html")

