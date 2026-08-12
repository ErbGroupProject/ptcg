from django.urls import path
from . import views


app_name="shops"
urlpatterns=[
    path('shop/',views.shop,name='shop'),
    path('search_shops/',views.search_shops,name='search_shops'),
]
