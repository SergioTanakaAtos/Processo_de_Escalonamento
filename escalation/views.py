from django.shortcuts import render
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from .models import LogPermission
from django.shortcuts import get_object_or_404

from django.http import HttpResponseForbidden
# Create your views here.
def initial_page(request):
    #pylint: disable=E1101
    groups = Group.objects.all()
    user = request.user
    group_states = {} 
    states_mapping = {None: "Permissão pendente", True: "Permitido", False: "Não pediu permissão"}

    for group in groups:
        log_per, created = LogPermission.objects.get_or_create(group=group, user=user)
        user_group = UserGroupDefault.objects.filter(group=group, user=user).first()
        if user_group.is_visualizer:
            log_per.is_active = True
        if created:
            log_per.save()

        group_states[group] = states_mapping.get(log_per.is_active, "Não pediu permissão")
    return render(request, 'escalation/initial_page.html', {'group_states': group_states})

def escalation(request, group_id, user_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    
    user_group_default = get_object_or_404(UserGroupDefault, user=user, group=group)

    if not user_group_default.is_visualizer:
        return HttpResponseForbidden("Você não tem permissão para visualizar este cliente.")
    

    escalation = Escalation.objects.filter(group=group)
    
    if not escalation:
        return render(request, 'escalation/escalation_page.html', {'group': group, 'message': "Não há escalonamento cadastrado para este grupo."})
    return render(request, 'escalation/escalation_page.html', {'group': group, 'escalation': escalation})

def create_escalation(request, group_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        position = request.POST.get('position')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        level = request.POST.get('level')
        area = request.POST.get('area')
        service = request.POST.get('service')
        escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
        escalation.save()
    return render(request, 'escalation/create_escalation.html', {'group': group})