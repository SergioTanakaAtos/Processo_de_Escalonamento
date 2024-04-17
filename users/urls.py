from django.urls import path 
from . import views
from escalation.views import initial_page

urlpatterns = [
    path('', views.index, name='index'),
\
]
