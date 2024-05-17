from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('management/', views.get_users, name='management'),
    path('register/', views.register, name="register"),
    path('cadastro-exemplo/', views.cadastro_exemplo, name='cadastro-exemplo')
]
