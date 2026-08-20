from django.shortcuts import render, get_object_or_404
#from shops.models import Shoplist
from .models import Tradelist
from django.contrib import messages

def trade_lists(request):
    #tradelists = Tradelist.objects.filter(is_sold=False).order_by("-list_date")
    trade_images = [
        'image/sm_banner_01.jpg',
        'image/sm_banner_02.png',
        'image/sm_banner_03.png',
        'image/sm_banner_04.jpg',
        'image/sm_banner_05.png',
        'image/sm_banner_06.jpg',
        ]

    context = {
        "trade_images":trade_images,
        
        #"tradelists" : tradelists,
        }
    return render(request, "trades/trade_lists.html", context)

def trade_item(request, tradelist_id):
    tradelist = get_object_or_404(Tradelist, id=tradelist_id)
    context = {"tradelist" : tradelist,}
    return render(request, "trades/trade_item.html", context)

def create_new_trade_post(request):
    if not request.user.is_authenticated:
        return redirect(LOGIN_URL)

#    if request.method =="POST":
        form = TradelistForm(request.POST)
        if form.is_valid():
            tradelist = form.save(commit=False)
            tradelist.username = request.username
            tradelist.save()
            messages.success(request, "Your item has posted!")
            return redirect("tradelists:trade_item",tradelist.id)
#    else:
        form = ContactForm()

#    context = {"form":form,}

    return render(request,"trade/create_new_trade_post.html")

def edit_trade_post(request,tradelist_id):
    if not request.user.is_authenticated:
        return redirect(LOGIN_URL)

#    tradelist = get_object_or_404(Tradelist, id=tradelist_id)

#    if request.username != listing.username:
        messages.error(request, "You don't have the right to edit this post!")
        return redirect("tradelists:detail", tradelist.id)

#    if request.method == "POST":
        form = ContactForm(request.POST, instance=tradelist)
#    if form.is_valid():
        form.save()
        messages.success(request, "Post has renewed.")
        return redirect("tradelists:detail", tradelist.id)
#    else:
        form = ContactForm(instance=tradelist)

    return render(request, "trades/edit_trade_post.html")