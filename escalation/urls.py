from django.urls import path 
from . import views

urlpatterns = [
    path('', views.initial_page, name='initial_page'),
    path('escalation/<int:group_id>/<int:user_id>/', views.escalation, name='escalation'),
    path('create_escalation/<int:group_id>', views.create_escalation, name='create_escalation'),
]