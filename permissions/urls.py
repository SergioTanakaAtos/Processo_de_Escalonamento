from django.urls import path 
from . import views

urlpatterns = [
    path('', views.permissions, name='permissions'),
    path('create/<int:group_id>', views.save_permission, name='create-permission'),
    path('accepted/<int:permission_id>', views.accepted_permission, name='accepted'),
    path('denied/<int:permission_id>', views.denied_permission, name='denied'),
    
]