from django.shortcuts import render
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from django.shortcuts import get_object_or_404

from django.http import HttpResponseForbidden
# Create your views here.
def initial_page(request):
    groups = Group.objects.all()
    return render(request, 'escalation/initial_page.html', {'groups': groups})

def escalation(request, group_id, user_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)

    user_group_default = get_object_or_404(UserGroupDefault, user=user, group=group)

    if not user_group_default.is_visualizer:
        return HttpResponseForbidden("Você não tem permissão para visualizar este cliente.")
    

    escalation = Escalation.objects.filter(group=group)
    
    if not escalation:
        return HttpResponseForbidden("Não há escalonamento cadastrado para este grupo.")
    return render(request, 'escalation/group_page.html', {'group': group, 'escalation': escalation})