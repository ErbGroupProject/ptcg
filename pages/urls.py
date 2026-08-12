from django.urls import path
from . import views

app_name="pages"
urlpatterns=[
    path('',views.home,name='home'),
    path('shops/',views.shops,name='shops'),
    path('index/',views.index,name='index'),
]
