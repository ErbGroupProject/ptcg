from django.urls import path
from . import views

app_name="shops"
urlpatterns=[
    path('shop<int:slist_id>',views.shop,name='shop'),
    path('search_shops',views.search_shops,name='search_shops'),
    path('shop_list',views.shop_list,name='shop_list'),
]
