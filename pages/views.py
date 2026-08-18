from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, "pages/home.html")

def shops(request):
    return render(request, "pages/shops.html")

<<<<<<< HEAD
def index(request):
    return render(request, "pages/index.html")
=======
def trade(request):
    return render(request, "pages/trade.html")


def contact(request):
    return render(request, "pages/contact.html")


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



>>>>>>> origin/Johnny
