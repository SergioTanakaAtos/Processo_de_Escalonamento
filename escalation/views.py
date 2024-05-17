from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from .models import LogPermission
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test

from django.http import HttpResponseForbidden
from django.http import JsonResponse    
import os
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
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
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def save_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            group_name_lower = group_name.lower()
            if Group.objects.filter(name__iexact=group_name_lower).exists():
                return JsonResponse({'message':'O nome do grupo já existe.'}, status=400)
            group = Group(name=group_name)
            group.save()
            return JsonResponse({'message':'Grupo criado com sucesso.'}, status=200)
        else:
            return JsonResponse({'message':'O nome do grupo não pode estar vazio.'}, status=400)
    return JsonResponse({'message':'Método não permitido.'}, status=405)
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def edit_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        new_group_name = request.POST.get('new_company')
        group = Group.objects.get(id=group_id)
        group.name = new_group_name
        group.save()
        return JsonResponse({'message':'Grupo criado com sucesso.'}, status=200)
    
    return render(request, 'initial_page.html')     
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def load_data(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        
        upload_dir = os.path.join(settings.BASE_DIR, 'escalation/static/data')
                
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(csv_file.name, csv_file)
        
        file_path = fs.path(filename)
        df = pd.read_csv(file_path)
        df_group = df['group']
        if Group.objects.filter(name__in=df_group).exists():
            return JsonResponse({'message':'O nome do grupo já existe.'}, status=400)
        for index, row in df.iterrows():
            group_name = row['group']
            group = Group.objects.get(name=group_name)

            name = row['nome']
            position = row['position']
            phone = row['phone']
            email = row['email']
            level = row['level']
            area = row['area']
            service = row['service']
            if Escalation.objects.filter(group=group, name=name).exists():
                return JsonResponse({'message':'Já existe um escalonamento com este nome.'}, status=400)
            escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
            escalation.save()
        
        return JsonResponse({'message':'Grupos e escalations criados com sucesso.'}, status=200)
    
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
    return render(request, 'escalation/create_escalation.html', {'group': group})