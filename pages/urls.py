from django.urls import path
from . import views

app_name="pages"
urlpatterns=[
    path('',views.index,name='index'),
    #path('shops/',views.shops,name='shops'),
    # path('index/',views.index,name='index'),
]
