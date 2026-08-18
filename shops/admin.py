from django.contrib import admin
from .models import Shoplist

class ShoplistAdmin(admin.ModelAdmin):
    list_display = ('shopname','address')
    list_display_links =('shopname','address')
    search_fields = 'shopname','address',
    list_per_page = 25

admin.site.register(Shoplist,ShoplistAdmin)
