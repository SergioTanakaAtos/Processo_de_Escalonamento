from django.urls import path 
from . import views

urlpatterns = [
    path('', views.permissions, name='permissions'),
    path('create/<int:group_id>', views.save_permission, name='create-permission'),
    path('<str:action>/<int:permission_id>', views.action_permission, name='action-permission'),
]