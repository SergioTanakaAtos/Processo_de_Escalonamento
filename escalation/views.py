from django.shortcuts import render
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault

from django.http import HttpResponseForbidden
# Create your views here.
def initial_page(request):
    groups = Group.objects.all()
    return render(request, 'escalation/initial_page.html', {'groups': groups})

def escalation(request, group_id, user_id):
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    
    if not UserGroupDefault.objects.filter(user_id=user, group_id=group, is_visualizer=True).exists():
        return HttpResponseForbidden("Você não tem permissão para visualizar este cliente.")

    escalation = Escalation.objects.filter(group=group)
    
    return render(request, 'escalation/group_page.html', {'group': group, 'escalation': escalation})