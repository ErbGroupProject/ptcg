from django.shortcuts import render, redirect

# Create your views here.
def card_lists(request):
    return redirect("listings:card_listings")
