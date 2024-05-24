from django.urls import path 
from . import views
from .views import register

urlpatterns = [
<<<<<<< HEAD
<<<<<<< HEAD
    #path('', views.index, name='index'),
   # path('', views.index, name='login'),
    path('register/', views.register, name='register'),
    path('', views.login, name='login'),
=======
    path('', views.index, name='index'),
    path('management/', views.get_users, name='management'),
    path('register/', views.register, name="register"),
    path('cadastro-exemplo/', views.cadastro_exemplo, name='cadastro-exemplo'),
    path('get_groups/', views.get_user_groups, name='user_groups')
>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43
]
=======
    path('', views.index, name='index'),
    path('management/', views.get_users, name='management'),
    path('register/', views.register, name="register"),
    path('cadastro-exemplo/', views.cadastro_exemplo, name='cadastro-exemplo')
]
>>>>>>> 794d11a486a6c769dfa4245ccfec4cbf7ed6363c
