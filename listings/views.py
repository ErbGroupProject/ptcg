from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Profile
from cards.models import Card, Generation
from decks.models import Deck, DeckCard
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

    # 篩選（狀態 / 系列 / 交易地點）
    condition = request.GET.get('condition', '').strip()
    series = request.GET.get('series', '').strip()
    place = request.GET.get('place', '').strip()

    if condition:
        qs = qs.filter(condition=condition)
    if series:
        qs = qs.filter(series_name=series)
    if place:
        qs = qs.filter(deal_place=place)

    page_obj = Paginator(qs, 12).get_page(request.GET.get('page'))  # 4 個一行 × 3 行

    # 分頁保留所有篩選參數
    params = request.GET.copy()
    params.pop('page', None)
    query_string = params.urlencode()

    # 下拉選項（distinct）
    conditions = (
        Tradelist.objects.filter(is_sold=False)
        .exclude(condition='')
        .values_list('condition', flat=True)
        .distinct().order_by('condition')
    )
    series_list = (
        Tradelist.objects.filter(is_sold=False)
        .exclude(series_name='')
        .values_list('series_name', flat=True)
        .distinct().order_by('series_name')
    )
    places = (
        Tradelist.objects.filter(is_sold=False)
        .exclude(deal_place='')
        .values_list('deal_place', flat=True)
        .distinct().order_by('deal_place')
    )

    return render(request, 'listings/index.html', {
        'page_obj': page_obj,
        'q': q,
        'condition': condition,
        'series': series,
        'place': place,
        'query_string': query_string,
        'conditions': conditions,
        'series_list': series_list,
        'places': places,
    })


def card_listings(request):
    """卡片列表（Card）"""
    qs = (
        Card.objects
        .select_related('generation')               # card_number_display 會用到 generation
        .order_by('generation', 'card_number')
    )

    # 搜尋
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(category__icontains=q) |
            Q(stage__icontains=q) |
            Q(rarity__icontains=q) |
            Q(energy_type__icontains=q)
        )

    # 篩選
    category = request.GET.get('category', '').strip()
    energy = request.GET.get('energy', '').strip()
    stage = request.GET.get('stage', '').strip()
    rarity = request.GET.get('rarity', '').strip()
    gen = request.GET.get('gen', '').strip()

    if category:
        qs = qs.filter(category=category)
    if energy:
        qs = qs.filter(energy_type=energy)
    if stage:
        qs = qs.filter(stage=stage)
    if rarity:
        qs = qs.filter(rarity=rarity)
    if gen:
        qs = qs.filter(generation_id=gen)

    page_obj = Paginator(qs, PAGE_SIZE).get_page(request.GET.get('page'))

    # 分頁保留所有篩選參數
    params = request.GET.copy()
    params.pop('page', None)
    query_string = params.urlencode()

    context = {
        'page_obj': page_obj,
        'q': q,
        'category': category,
        'energy': energy,
        'stage': stage,
        'rarity': rarity,
        'gen': gen,
        'query_string': query_string,
        'categories': Card.objects.values_list('category', flat=True).exclude(category='').distinct().order_by('category'),
        'energies': Card.objects.values_list('energy_type', flat=True).exclude(energy_type='').distinct().order_by('energy_type'),
        'stages': Card.objects.values_list('stage', flat=True).exclude(stage='').distinct().order_by('stage'),
        'rarities': Card.objects.values_list('rarity', flat=True).exclude(rarity='').distinct().order_by('rarity'),
        'generations': Generation.objects.all().order_by('name'),
    }

    # Deck
    if request.user.is_authenticated:
        decks = Deck.objects.filter(
            user=request.user
        ).order_by("id")

        selected_deck_id = request.session.get(
            "selected_deck_id"
        )

        selected_deck = decks.filter(
            id=selected_deck_id
        ).first()

        if selected_deck is None:
            selected_deck = decks.first()

        if selected_deck:
            request.session["selected_deck_id"] = selected_deck.id

        context["decks"] = decks
        context["selected_deck"] = selected_deck
        
    else:
        context["decks"] = []
        context["selected_deck"] = None
        context["available_cards"] = []


    # THIS MUST BE AT THE END OF card_listings()
    return render(
        request,
        "listings/card_listings.html",
        context
    )

def card_detail(request, card_id):
    """卡片詳情"""
    card = get_object_or_404(
        Card.objects.select_related('generation').prefetch_related(
            'abilities',
            'attacks__energy_costs',
            'weaknesses',
            'resistances',
            'retreats',
        ),
        id=card_id,
    )
    context = {'card': card}
    if request.user.is_authenticated:
        context['my_decks'] = Deck.objects.filter(user=request.user)
    else:
        context['my_decks'] = []
    return render(request, 'listings/card_listing.html', context)


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


