from django.urls import path
from . import views

app_name="trades"
urlpatterns=[
    path('trade_lists/',views.trade_lists,name='trade_lists'),
    path('trades_item/',views.trade_item,name='trade_item'),
    path('create_new_trade_post/',views.create_new_trade_post,name='create_new_trade_post'),
    path('edit_trade_post/',views.edit_trade_post,name="edit_trade_post")
]
