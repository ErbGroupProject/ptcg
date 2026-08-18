from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Shoplist
from django.db.models import Q

def shop(request,listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    context = {
        "listing":listing,
    }
    return render(request, "shops/shop.html",context)

def search_shops(request):
    queryset_list = Shoplist.objects.all

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(Q(description__icontains=keywords) | Q(title__icontains=keywords))
    if 'district' in request.GET:
            district = request.GET['district']
            if district:
                queryset_list = queryset_list.filter(Q(district__iexact=district))
    paginator = Paginator(queryset_list, 25)
    page_number = request.GET.get('page)')
    paged_listings = paginator.get_page(page_number)
    get_params = request.GET.copy()
    get_params.pop('page',None)
    clean_query = get_params.urlencode()
    context = {
        "listings" : paged_listings,
        "clean_query" : clean_query,
    }

    return render(request, "shops/search_shops.html",context)

