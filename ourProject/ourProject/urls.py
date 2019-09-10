from django.contrib import admin
from django.urls import path, include
from backer import views


urlpatterns = [
    path(r'admin/', admin.site.urls),
    path('data/', views.DataTest),
    path('login/', views.login),

    # 数据库增删改查示例
    path('insertPerson/', views.insertPerson),
    path('delPerson/', views.delPerson),
    path('updatePerson/', views.updatePerson),
    path('listPerson/', views.listPerson)
]
