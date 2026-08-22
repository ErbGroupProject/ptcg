from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q

from contacts.models import Chat, Message
from tradings.models import TradingRecord
from cards.models import Card
from decks.models import Deck, DeckCard


from .forms import ProfileForm
from .models import Profile


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username", "").strip()

        # 檢查 username 是否被別人使用（避免 IntegrityError 500）
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "這個用戶名稱已被使用")
            return redirect("accounts:edit_profile")

        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.username = username
        user.email = request.POST.get("email", "")
        user.save()

        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {"form": form})


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "That username is taken")
                return redirect("accounts:register")
            elif User.objects.filter(email=email.lower()).exists():
                messages.error(request, "That email is being used")
                return redirect("accounts:register")
            else:
                new_user = User.objects.create_user(
                    username=username,
                    email=email.lower(),
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                Profile.objects.create(user=new_user)
                messages.success(request, "You are now registered and can log in")
                return redirect("accounts:login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("accounts:register")

    return render(request, "accounts/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "User name or password does not right! Please try again!")
            return redirect("accounts:login")
    return render(request, "accounts/login.html")


def logout(request):
    if request.method == "POST":
        auth.logout(request)
    return redirect("pages:index")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


def _review_state(chat, user):
    # 注意：不再用 trade_finished 短路。
    # 交易完成（確認交易）與評價（雙方互評）是兩個獨立維度，
    # 即使交易已完成，雙方仍應能評價。
    record = TradingRecord.objects.filter(chat=chat).first()
    if record is None:
        return "none"           # 白色：都還沒評
    my_star = record.buyer_star if user == chat.buyer else record.seller_star
    other_star = record.seller_star if user == chat.buyer else record.buyer_star
    if my_star is not None and other_star is not None:
        return "done"           # 灰色：雙方都評完
    elif my_star is not None:
        return "waiting_other"  # 我已評，等對方 → 灰「等待對方評價」
    elif other_star is not None:
        return "waiting_me"     # 對方已評，等我 → 藍「等待評價」
    return "none"


@login_required
def dashboard(request):
    user = request.user
    active_tab = request.GET.get('tab', 'buying')

    all_qs = Chat.objects.filter(Q(buyer=user) | Q(seller=user), is_spam=False).order_by("-updated_at")
    all_chats = Paginator(all_qs, 7).get_page(request.GET.get("all_page", 1))

    buying_qs = Chat.objects.filter(buyer=user, trade_finished=False, is_spam=False)
    buying_chats = Paginator(buying_qs, 7).get_page(request.GET.get("buy_page", 1))

    selling_qs = Chat.objects.filter(seller=user, trade_finished=False, is_spam=False)
    selling_chats = Paginator(selling_qs, 7).get_page(request.GET.get("sell_page", 1))

    completed_qs = Chat.objects.filter(Q(buyer=user) | Q(seller=user), trade_finished=True, is_spam=False)
    completed_chats = Paginator(completed_qs, 7).get_page(request.GET.get("done_page", 1))

    spam_qs = Chat.objects.filter(Q(buyer=user) | Q(seller=user), is_spam=True).order_by("-updated_at")
    spam_chats = Paginator(spam_qs, 7).get_page(request.GET.get("spam_page", 1))
    
    
    # Deck 優化：查詢使用者的牌組與牌組卡片
    decks = Deck.objects.filter(user=request.user).order_by("id")
    deck_cards = DeckCard.objects.filter(deck__user=request.user).select_related("card")

    # 記住選中的牌組（session）
    selected_deck_id = request.session.get("selected_deck_id")
    selected_deck = decks.filter(id=selected_deck_id).first()
    if selected_deck is None:
        selected_deck = decks.first()
    if selected_deck:
        request.session["selected_deck_id"] = selected_deck.id

    for chat in all_chats:
        chat.review_state = _review_state(chat, user)
    for chat in buying_chats:
        chat.review_state = _review_state(chat, user)
    for chat in selling_chats:
        chat.review_state = _review_state(chat, user)
    for chat in completed_chats:
        chat.review_state = _review_state(chat, user)

    return render(request, "accounts/dashboard.html", {
        "all_chats": all_chats,
        "buying_chats": buying_chats,
        "selling_chats": selling_chats,
        "completed_chats": completed_chats,
        "spam_chats": spam_chats,
        "active_tab": active_tab,
        "decks": decks,
        "deck_cards": deck_cards,
        "selected_deck": selected_deck,
    })
