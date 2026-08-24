from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Shoplist
from .choices import district_choices
import urllib.parse


def shop(request, slist_id):
    """店鋪詳情"""
    slist = get_object_or_404(Shoplist, pk=slist_id)
    encoded_address = urllib.parse.quote(slist.address)
    map_url = f'https://www.google.com/maps?q={encoded_address}&output=embed'
    context = {'slist': slist, 'map_url': map_url}
    return render(request, "shops/shop.html", context)


def _apply_district(queryset_list, district):
    """把下拉選單傳進來的中文分區，轉成資料庫裡的英文分區再篩選。

    district_choices 是 {中文分區: 英文分區} 的對照表，
    下拉選單的選項值用的是中文 key，所以要先轉成英文 value 才能對上 DB。
    """
    if district and district != 'All':
        english = district_choices.get(district, district)
        return queryset_list.filter(district__iexact=english)
    return queryset_list


def search_shops(request):
    """搜尋店鋪"""
    queryset_list = Shoplist.objects.all().order_by("id")

    keywords = request.GET.get('keywords', '').strip()
    district = request.GET.get('district', '').strip()

    if keywords:
        queryset_list = queryset_list.filter(
            Q(shopname__icontains=keywords) |
            Q(address__icontains=keywords) |
            Q(website__icontains=keywords)
        )
    queryset_list = _apply_district(queryset_list, district)

    paginator = Paginator(queryset_list, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)

    context = {
        "shoplist": paged_listings,
        "values": {"keywords": keywords, "district": district},
        "district_choices": district_choices,
    }
    return render(request, "shops/search_shops.html", context)


def shop_list(request):
    """店鋪列表（含搜尋）"""
    queryset_list = Shoplist.objects.all().order_by("id")

    keywords = request.GET.get('keywords', '').strip()
    district = request.GET.get('district', '').strip()

    if keywords:
        queryset_list = queryset_list.filter(
            Q(shopname__icontains=keywords) |
            Q(address__icontains=keywords) |
            Q(website__icontains=keywords)
        )
    queryset_list = _apply_district(queryset_list, district)

    paginator = Paginator(queryset_list, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)

    context = {
        "shoplist": paged_listings,
        "values": {"keywords": keywords, "district": district},
        "district_choices": district_choices,
    }
    return render(request, "shops/shop_list.html", context)
