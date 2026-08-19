from django.urls import path
from . import views

app_name = "listings"

urlpatterns = [
    path("", views.index, name="index"),
    path("my/", views.my_listings, name="my_listings"),
    path("create/", views.create, name="create"),
    path("cards/", views.card_listings, name="card_listings"),
    path("<int:listing_id>/", views.detail, name="detail"),
    path("<int:listing_id>/edit/", views.edit, name="edit"),
    path("<int:listing_id>/delist/", views.delist, name="delist"),
    path("seller/<int:user_id>/", views.seller_profile, name="seller_profile"),

]
