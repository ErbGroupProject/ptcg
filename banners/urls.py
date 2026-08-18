from django.urls import path
from . import views


app_name = "banners"
urlpatterns = [
    # 即使目前沒有路由，也必須保留一個空的 list 或是寫好路徑
    path('', views.index, name='index'),
    
]


# def index(request):
#     banners = BannersItem.objects.all()
#     return render(request, "banners/index.html", {"banners_list": banners})




