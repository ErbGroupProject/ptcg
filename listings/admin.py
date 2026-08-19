from django.contrib import admin
from .models import Tradelist

class TradelistAdmin(admin.ModelAdmin):
    list_display = ('sell_item_name','user_name','sell_item_main_photo','price','descriptions','is_sold','list_date','condition')
    list_display_links = ('sell_item_name','user_name','list_date')
    search_fields = ('sell_item_name','user_name','price','list_date')
    list_per_page = 25
    list_editable = ('descriptions','sell_item_main_photo','price','condition')

admin.site.register(Tradelist,TradelistAdmin)