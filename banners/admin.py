from django.contrib import admin
from .models import BannersItem

class BannersItemAdmin(admin.ModelAdmin):
    list_display = "banner_id", "photo_banner", "url_link"
    list_display_links = "banner_id", "photo_banner","url_link"
    
    list_per_page = 20

admin.site.register(BannersItem, BannersItemAdmin)
