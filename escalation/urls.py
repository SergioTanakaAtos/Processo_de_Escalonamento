from django.urls import path 
from . import views

urlpatterns = [
    path('', views.initial_page, name='initial_page'),
    path('save_group/', views.save_group, name='save_group'),
    path('edit_group/',views.edit_group,name='edit_group'),
    path('escalation/<int:group_id>/<int:user_id>/', views.escalation, name='escalation'),
    path('create_escalation/<int:group_id>', views.create_escalation, name='create_escalation'),
    path('load_data/', views.load_data, name='load_data'),
]