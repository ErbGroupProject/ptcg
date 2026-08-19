from django.contrib import admin
from .models import TradingRecord

class TradingRecordAdmin(admin.ModelAdmin):
    list_display = "chat","created_at"
    list_display_links = "chat","created_at"
    search_fields = "chat","created_at"
    list_per_page = 25

admin.site.register(TradingRecord,TradingRecordAdmin)
