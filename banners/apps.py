from django.apps import AppConfig
from django.shortcuts import render
from django.http import HttpResponse


class BannersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banners'
    #return render

def index(request):
    return render(request, "banners/index.html")

