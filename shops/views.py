from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Shoplist
from django.db.models import Q
from .choices import district_choices
import urllib

def shop(request,slist_id):
    slist = get_object_or_404(Shoplist, pk=slist_id)
    encoded_address = urllib.parse.quote(slist.address)
    map_url = f'https://google.com{encoded_address}&output=embed'
    context = {'slist':slist,
        'map_url':map_url,}
    return render(request, "shops/shop.html",context)

def search_shops(request):
    queryset_list = Shoplist.objects.all()
    distinct_districts = Shoplist.objects.filter(district__isnull=False).exclude(district='').values_list('district', flat=True).distinct().order_by('district')

    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(Q(description__icontains=keywords) | Q(title__icontains=keywords))
    selected_district = request.GET.get('district', '')
    if selected_district and selected_district != 'All':
        queryset_list = queryset_list.filter(district__iexact=selected_district)

    paginator = Paginator(queryset_list, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)
    get_params = request.GET.copy()
    get_params.pop('page',None)
    clean_query = get_params.urlencode()
    context = {
        "listings" : paged_listings,
        "clean_query" : clean_query,
        "district_choices":district_choices,
    }

    return render(request, "shops/search_shops.html",context)

def shop_list(request):
    shoplist = Shoplist.objects.all()
    paginator = Paginator(shoplist, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)
    context = {"shoplist" : paged_listings,
        "district_choices":district_choices,
        }
    return render(request,"shops/shop_list.html",context)

