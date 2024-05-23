from django.urls import path 
from . import views
from .views import register

urlpatterns = [
    #path('', views.index, name='index'),
   # path('', views.index, name='login'),
    path('register/', views.register, name='register'),
    path('', views.login, name='login'),
]