from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone','bio')
    list_display_links = (('user','bio'))
    search_fields = ('user','phone')
    list_per_page = 25

admin.site.register(Profile, ProfileAdmin)
