from django.shortcuts import render, redirect

# Create your views here.
<<<<<<< HEAD
def index(request):
    return redirect("listings:card_listings")
=======
def card_lists(request):
    return render(request, "cards/card_listings.html")
>>>>>>> tuv
