from django.urls import path
from . import views
 
urlpatterns = [

    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('get_groups/', views.get_user_groups, name='user_groups'),
    path('management/', views.get_users, name='management'),    
    path('update-user-groups/', views.update_user_groups, name='update-user-groups'),
    # path('update-level-user/', views.update_level_user, name='update-level-user')
    
]
 