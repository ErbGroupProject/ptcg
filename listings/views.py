from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Profile
from cards.models import Card
from .models import Tradelist
from .forms import ListingForm
from django.db.models import Avg
from tradings.models import TradingRecord
from django.db.models import Q, Max, Case, When, Value, IntegerField, F




PAGE_SIZE = 9  # 3 列 × 每列 3 個


from django.contrib.auth.decorators import login_required


@login_required
def create(request):
    """新增刊登"""
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user_name = Profile.objects.get(user=request.user)
            listing.save()
            return redirect('listings:detail', listing_id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})


@login_required
def my_listings(request):
    """我的刊登"""
    profile = Profile.objects.get(user=request.user)
    listings = (
        Tradelist.objects
        .filter(user_name=profile)
        .prefetch_related('chat_room__buyer')
        .prefetch_related('chat_room')
        .order_by('-list_date')
    )
    completed_listings = listings.filter(chat_room__trade_finished=True).distinct()
    return render(request, 'listings/my_listing.html', {
        'listings': listings,
        'completed_listings': completed_listings,
    })

def index(request):
    """上架商品列表（Tradelist）"""
    qs = (
        Tradelist.objects
        .filter(is_sold=False)
        .select_related('user_name__user')
        .prefetch_related('chat_room')
        .annotate(
            completed_at=Max('chat_room__updated_at',
                             filter=Q(chat_room__trade_finished=True)),
        )
        .annotate(
            is_completed=Case(
                When(completed_at__isnull=True, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            sort_time=Case(
                When(completed_at__isnull=True, then=F('list_date')),
                default=F('completed_at'),
            ),
        )
        .order_by('is_completed', '-sort_time')
    )

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(sell_item_name__icontains=q) |
            Q(series_name__icontains=q) |
            Q(series_number__icontains=q) |
            Q(condition__icontains=q) |
            Q(descriptions__icontains=q) |
            Q(user_name__user__username__icontains=q)
        )

    page_obj = Paginator(qs, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'listings/index.html', {'page_obj': page_obj, 'q': q})


def card_listings(request):
    """卡片列表（Card）"""
    qs = (
        Card.objects
        .select_related('generation')               # card_number_display 會用到 generation
        .order_by('generation', 'card_number')
    )

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(category__icontains=q) |
            Q(stage__icontains=q) |
            Q(rarity__icontains=q) |
            Q(energy_type__icontains=q)
        )

    page_obj = Paginator(qs, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'listings/card_listing.html', {'page_obj': page_obj, 'q': q})


def detail(request, listing_id):
    """商品詳情"""
    listing = get_object_or_404(
        Tradelist.objects.select_related('user_name__user'),
        id=listing_id,
    )
    return render(request, 'listings/detail.html', {'listing': listing})


def edit(request, listing_id):
    """編輯刊登（僅賣家本人可編輯）"""
    listing = get_object_or_404(Tradelist, id=listing_id)

    # 所有權檢查
    if listing.user_name.user != request.user:
        return redirect('listings:detail', listing_id=listing.id)

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('listings:detail', listing_id=listing.id)
    else:
        form = ListingForm(instance=listing)

    return render(request, 'listings/edit.html', {'form': form, 'listing': listing})


def delist(request, listing_id):
    """下架商品（只用 POST 變更狀態）"""
    listing = get_object_or_404(Tradelist, id=listing_id)

    if request.method == 'POST':
        # 所有權檢查：只有賣家能下架自己的商品
        if listing.user_name.user == request.user:
            listing.is_sold = True
            listing.save()
        return redirect('listings:index')

    return redirect('listings:detail', listing_id=listing.id)

def seller_profile(request, user_id):
    """賣家個人頁"""
    seller = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=seller)

    # 買家對這個賣家的評價
    records = TradingRecord.objects.filter(
        chat__seller=seller,
        buyer_star__isnull=False,
    ).select_related('chat').order_by('-id')

    review_count = records.count()
    avg_star = records.aggregate(Avg('buyer_star'))['buyer_star__avg'] or 0

    return render(request, 'listings/seller_profile.html', {
        'seller': seller,
        'profile': profile,
        'records': records,
        'review_count': review_count,
        'avg_star': avg_star,
    })


