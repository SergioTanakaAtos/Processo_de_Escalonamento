from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from .models import LogPermission
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponseForbidden
from django.http import HttpResponse    
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

@csrf_exempt
def save_group(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        if request.method == 'POST':
            group_name = request.POST.get('group_name')
            group = Group(name=group_name)
            group.save()
            return HttpResponse(200, 'Grupo criado com sucesso.')
    return HttpResponse(403, {'message':'Você não tem permissão para criar grupos.'})

def edit_group(request, group_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group.name = group_name
        group.save()
        return redirect('initial_page')
            
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
        if Escalation.objects.filter(group=group, name=name).exists():
            return redirect('escalation/create_escalation.html', {'group': group, 'message': 'Já existe um escalonamento com este nome.'})
        else:
            position = request.POST.get('position')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            area = request.POST.get('area')
            service = request.POST.get('service')
            level = request.POST.get('level')
            escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
            
            escalation.save()
    return render(request, 'escalation/create_escalation.html', {'group': group})