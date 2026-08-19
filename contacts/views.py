from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from listings.models import Tradelist
from .models import Chat, Message


@login_required
def start_chat_from_listing(request, listing_id):
    listing = get_object_or_404(Tradelist, id=listing_id)
    seller = listing.user_name.user
    buyer = request.user

    if buyer == seller:
        return redirect("listings:detail", listing.id)

    chat, created = Chat.objects.get_or_create(
        listing=listing,
        buyer=buyer,
        seller=seller,
    )
    return redirect("contacts:chat_detail", chat.id)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.buyer, chat.seller]:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        content = request.POST.get("message", "").strip()
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
        return redirect("contacts:chat_detail", chat.id)

    # GET：把對方訊息標為已讀
    Message.objects.filter(chat=chat).exclude(sender=request.user).update(is_read=True)

    message_list = chat.messages.all()
    return render(request, "contacts/chat_detail.html", {
        "chat": chat,
        "message_list": message_list,
    })


@login_required
def mark_as_spam(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user == chat.buyer:
        chat.is_spam = True
        chat.save()
    return redirect("accounts:dashboard")


@login_required
def unmark_spam(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user == chat.buyer:
        chat.is_spam = False
        chat.save()
    return redirect("accounts:dashboard")
