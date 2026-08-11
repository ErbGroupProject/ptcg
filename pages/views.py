from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, "pages/home.html")

def shops(request):
    return render(request, "pages/shops.html")

def index(request):
    return render(request, "pages/index.html")
