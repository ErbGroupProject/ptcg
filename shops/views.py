from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Shoplist
from django.db.models import Q
from .choices import district_choices, district_list_for_frontend
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
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(Q(shopname__icontains=keywords))
    selected_district = request.GET.get('district', '')
    if selected_district and selected_district != '':
        try:
            idx = int(selected_district)
            target_item = district_list_for_frontend[idx]
            db_district_value = target_item[0]
            queryset_list = queryset_list.filter(district__iexact=db_district_value)
            
            print(f"🎯 數字索引匹配成功！選中了第 {idx} 項：{target_item[1]} ({db_district_value})")
        except (ValueError, IndexError):
            pass

    paginator = Paginator(queryset_list, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)
    get_params = request.GET.copy()
    get_params.pop('page',None)
    clean_query = get_params.urlencode()
    context = {
        "searched_shoplists" : paged_listings,
        "clean_query" : clean_query,
        "district_choices":district_list_for_frontend,
        "selected_district":selected_district,
    }
    return render(request, "shops/search_shops.html",context)

def shop_list(request):
    shoplist = Shoplist.objects.all()
    paginator = Paginator(shoplist, 25)
    page_number = request.GET.get('page')
    paged_listings = paginator.get_page(page_number)
    context = {"shoplist" : paged_listings,
        "district_choices":district_list_for_frontend,
        }
    return render(request,"shops/shop_list.html",context)

