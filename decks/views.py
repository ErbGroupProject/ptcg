from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect

from cards.models import Card
from .models import Deck
from . import services


@login_required
def add_card(request, card_id):
    """把卡片加入牌組（卡片詳情頁的 ＋ 按鈕）"""
    card = get_object_or_404(Card, id=card_id)
    if request.method == "POST":
        deck_id = request.POST.get("deck_id")
        deck = get_object_or_404(Deck, id=deck_id, user=request.user)
        try:
            services.add_card_to_deck(deck, card, quantity=1)
            messages.success(request, f"已把「{card.title}」加入牌組「{deck.name}」")
        except ValidationError as exc:
            msg = exc.messages[0] if exc.messages else str(exc)
            messages.error(request, msg)
    return redirect("listings:card_detail", card.id)


@login_required
def create_deck(request):
    """建立新牌組（Deck1、Deck2...）"""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "請輸入牌組名稱")
        else:
            Deck.objects.create(user=request.user, name=name)
            messages.success(request, f"已建立牌組「{name}」")
    return redirect("listings:card_listings")


@login_required
def rename_deck(request, deck_id):
    """修改牌組名稱"""
    deck = get_object_or_404(Deck, id=deck_id, user=request.user)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "請輸入牌組名稱")
        else:
            deck.name = name
            deck.save()
            messages.success(request, f"已改名為「{name}」")
    return redirect("listings:card_listings")
