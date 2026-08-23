from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Shoplist
from .choices import district_list_for_frontend
import urllib.parse


def shop(request, slist_id):
    """店鋪詳情"""
    slist = get_object_or_404(Shoplist, pk=slist_id)
    encoded_address = urllib.parse.quote(slist.address)
    map_url = f"https://www.google.com/maps?q={encoded_address}&output=embed"

    context = {
        "slist": slist,
        "map_url": map_url,
    }
    return render(request, "shops/shop.html", context)


def search_shops(request):
    """搜尋店鋪"""
    queryset_list = Shoplist.objects.all()

    keywords = request.GET.get("keywords", "").strip()
    selected_district = request.GET.get("district", "").strip()

    if keywords:
        queryset_list = queryset_list.filter(
            Q(shopname__icontains=keywords)
            | Q(address__icontains=keywords)
            | Q(website__icontains=keywords)
        )

    if selected_district and selected_district != "All":
        district_value = selected_district

        try:
            index = int(selected_district)
            district_value = district_list_for_frontend[index][0]
        except (ValueError, IndexError):
            pass

        queryset_list = queryset_list.filter(
            district__iexact=district_value
        )

    paginator = Paginator(queryset_list, 25)
    paged_listings = paginator.get_page(request.GET.get("page"))

    get_params = request.GET.copy()
    get_params.pop("page", None)

    context = {
        "shoplist": paged_listings,
        "searched_shoplists": paged_listings,
        "values": {
            "keywords": keywords,
            "district": selected_district,
        },
        "selected_district": selected_district,
        "clean_query": get_params.urlencode(),
        "district_choices": district_list_for_frontend,
    }

    return render(request, "shops/search_shops.html", context)


def shop_list(request):
    """店鋪列表（含搜尋）"""
    queryset_list = Shoplist.objects.all()

    keywords = request.GET.get("keywords", "").strip()
    district = request.GET.get("district", "").strip()

    if keywords:
        queryset_list = queryset_list.filter(
            Q(shopname__icontains=keywords)
            | Q(address__icontains=keywords)
            | Q(website__icontains=keywords)
        )

    if district and district != "All":
        queryset_list = queryset_list.filter(
            district__iexact=district
        )

    paginator = Paginator(queryset_list, 25)
    paged_listings = paginator.get_page(request.GET.get("page"))

    context = {
        "shoplist": paged_listings,
        "values": {
            "keywords": keywords,
            "district": district,
        },
        "district_choices": district_list_for_frontend,
    }

    return render(request, "shops/shop_list.html", context)