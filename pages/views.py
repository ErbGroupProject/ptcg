from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, "pages/home.html")

def shops(request):
    return render(request, "pages/shops.html")

def index(request):
    #come form banners
    banner_images = [
        'image/banner_01.jpg',
        'image/banner_02.jpg',
        'image/banner_03.png',
        ]
    
    context = {
        'banner_images': banner_images
        }
    return render(request, "pages/index.html", context)
