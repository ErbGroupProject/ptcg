from django.shortcuts import render

# Create your views here.
def card_lists(request):
    return render(request, "cards/card_listings.html")