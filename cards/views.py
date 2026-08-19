from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return redirect("listings:card_listings")