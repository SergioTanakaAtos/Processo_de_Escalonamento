from django.urls import path 
from . import views

urlpatterns = [
    path('', views.initial_page, name='initial_page')
]