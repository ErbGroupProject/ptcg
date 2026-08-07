from django.urls import path
from . import views

app_name = "filters"
urlpatterns = [
    path('filters/', views.register, name='filters'),

]