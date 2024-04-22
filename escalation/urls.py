from django.urls import path 
from . import views

urlpatterns = [
    path('', views.initial_page, name='initial_page'),
    path('escalation/group/<int:group_id>/<int:user_id>/', views.escalation, name='escalation'),
]