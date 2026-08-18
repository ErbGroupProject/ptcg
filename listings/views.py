from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Profile
from .models import Tradelist
from .forms import TradelistForm
from django.contrib.auth.models import User
from tradings.models import TradingRecord



def index(request):
    listings = Tradelist.objects.filter(is_sold=False).order_by("-list_date")
    return render(request, "listings/index.html", {"listings": listings})


def detail(request, listing_id):
    listing = get_object_or_404(Tradelist, id=listing_id)
    return render(request, "listings/detail.html", {"listing": listing})



@login_required
def my_listings(request):
    user = request.user
    listings = Tradelist.objects.filter(user_name__user=user).order_by("-list_date")
    completed_listings = Tradelist.objects.filter(
        user_name__user=user, chat_room__trade_finished=True
    ).distinct().order_by("-list_date")

    return render(request, "listings/my_listings.html", {
        "listings": listings,
        "completed_listings": completed_listings,
    })


@login_required
def delist(request, listing_id):
    listing = get_object_or_404(Tradelist, id=listing_id)
    if request.user != listing.user_name.user:
        messages.error(request, "你沒有權限下架這個商品")
        return redirect("listings:my_listings")
    listing.is_sold = True
    listing.save()
    messages.success(request, "商品已下架")
    return redirect("listings:my_listings")


@login_required
def create(request):
    if request.method == "POST":
        form = TradelistForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            profile, _ = Profile.objects.get_or_create(user=request.user)
            listing.user_name = profile
            listing.save()
            messages.success(request, "商品已上架")
            return redirect("listings:detail", listing.id)
    else:
        form = TradelistForm()
    return render(request, "listings/create.html", {"form": form})


@login_required
def edit(request, listing_id):
    listing = get_object_or_404(Tradelist, id=listing_id)
    if request.user != listing.user_name.user:
        messages.error(request, "你沒有權限編輯這個商品")
        return redirect("listings:detail", listing.id)

    if request.method == "POST":
        form = TradelistForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "商品已更新")
            return redirect("listings:detail", listing.id)
    else:
        form = TradelistForm(instance=listing)

    return render(request, "listings/edit.html", {"form": form, "listing": listing})

def seller_profile(request, user_id):
    seller = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=seller)

    # 買家給賣家的評價
    records = list(
        TradingRecord.objects.filter(chat__seller=seller, buyer_star__isnull=False, is_public=True)
    )
    avg_star = round(sum(r.buyer_star for r in records) / len(records), 1) if records else 0

    return render(request, "listings/seller_profile.html", {
        "seller": seller,
        "profile": profile,
        "records": records,
        "avg_star": avg_star,
        "review_count": len(records),
    })
