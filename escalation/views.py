from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from .models import LogPermission
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user 

from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect   
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.contrib import messages
import json

@login_required(login_url='login')
def initial_page(request):
    #pylint: disable=E1101
    groups = Group.objects.all()
    user = request.user
    group_states = {} 
    states_mapping = {'desactivate': "Não pediu permissão", 'pending': "Permissão pendente", 'activate': "Permitido", 'denied': "Permissão negada"}
    for group in groups:
        log_per, created = LogPermission.objects.get_or_create(group=group, user=user)
        user_group = UserGroupDefault.objects.filter(group=group, user=user).first()
        if user_group is not None:
            if user_group.is_visualizer:
                log_per.status = 'activate'
                
            if created:
                log_per.save()

        group_states[group] = states_mapping.get(log_per.status, "Não pediu permissão")
    return render(request, 'escalation/initial_page.html', {'group_states': group_states})

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def save_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            group_name_lower = group_name.lower()
            if Group.objects.filter(name__iexact=group_name_lower).exists():
                messages.error(request, 'Já existe um grupo com este nome.')
                return HttpResponse(status=400)
            group = Group(name=group_name)
            group.save()
            messages.success(request, 'Grupo criado com sucesso.')
            return HttpResponse(status=200)
        else:
            messages.error(request, 'O nome do grupo não pode ser vazio.')
            return HttpResponse(status=400)
    messages.error(request, 'Método não permitido.')
    return HttpResponse(status=400)

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def edit_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        new_group_name = request.POST.get('new_company')
        if not new_group_name:
            messages.error(request, 'O nome do grupo não pode ser vazio.')
            return HttpResponse(status=400)
        group = Group.objects.get(id=group_id)
        group.name = new_group_name
        group.save()
        messages.success(request, 'Grupo editado com sucesso.')
        return HttpResponse(status=200)
    
    return render(request, 'initial_page.html')     

@csrf_exempt
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def load_data(request):    
    if request.method == 'POST':
        if 'xlsx_file' not in request.FILES:
            messages.error(request, 'Nenhum arquivo XLSX foi enviado.')
            return redirect('initial_page')

        xlsx_file = request.FILES['xlsx_file']

        try:
            # Diretório de upload
            upload_dir = os.path.join(settings.BASE_DIR, 'escalation/data')
            os.makedirs(upload_dir, exist_ok=True)

            # Salvando o arquivo enviado
            fs = FileSystemStorage(location=upload_dir)
            filename = fs.save(xlsx_file.name, xlsx_file)
            file_path = fs.path(filename)

            # Lendo o arquivo XLSX
            df = pd.read_excel(file_path, engine='openpyxl')

            # Verificação se o DataFrame está vazio
            if df.empty:
                messages.error(request, 'O arquivo XLSX está vazio.')
                os.remove(file_path)
                return redirect('initial_page')

            for index, row in df.iterrows():
                group_name = row['Empresa'].replace(' ', '')
                group, created = Group.objects.get_or_create(name=group_name)
                
                name = row['Nome'].replace(' ', '')
                position = row['Cargo']
                phone = row['Telefone'] if not pd.isnull(row['Telefone']) else ''
                email = row['Email']
                level = row['Nível']
                area = row['Área']
                service = row['Serviço']

                # Verifica se a entrada já existe antes de criar uma nova
                if not Escalation.objects.filter(name=name, group=group).exists():
                    escalation = Escalation(
                        name=name,
                        position=position,
                        phone=phone,
                        email=email,
                        level=level,
                        area=area,
                        service=service,
                        group=group
                    )
                    escalation.save()

            os.remove(file_path)

            messages.success(request, 'Dados carregados com sucesso.')
            return redirect('initial_page')

        except KeyError as e:
            messages.error(request, f'Erro ao carregar dados. Coluna ausente: {e}')
        except Exception as e:
            messages.error(request, f'Erro ao carregar dados: {str(e)}')

        return redirect('initial_page')

        
    messages.error(request, 'Método HTTP não suportado.')
    return redirect('initial_page')

@login_required(login_url='login')
def escalation(request, group_id, user_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    
    user_group_default = UserGroupDefault.objects.filter(group=group, user=user).first()
    if user_group_default is None:
        messages.error(request, 'Usuário não pertence a este grupo.')
        return redirect('initial_page')
    if not user_group_default.is_visualizer:
        messages.error(request, 'Usuário não tem permissão.')
        return redirect('initial_page')

    escalation = Escalation.objects.filter(group=group)
    if not escalation:
        messages.error(request, 'Não há escalonamento cadastrado para este grupo.')
        return render(request, 'escalation/escalation_page.html', {'group': group})
    return render(request, 'escalation/escalation_page.html', {'group': group, 'escalation': escalation})


@login_required(login_url='login')
def create_escalation(request, group_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if Escalation.objects.filter(group=group, name=name).exists():
            messages.error(request, 'Já existe um escalonamento com este nome.')
            return render(request,'escalation/create_escalation.html', {'group': group})
        else:
            position = request.POST.get('position')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            area = request.POST.get('area')
            service = request.POST.get('service')
            level = request.POST.get('level')
            escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
            
            escalation.save()
            messages.success(request, 'Escalonamento criado com sucesso.')
            return render(request, 'escalation/create_escalation.html', {'group': group})
    return render(request, 'escalation/create_escalation.html', {'group': group})

@login_required(login_url='login')
@csrf_exempt
def update_escalation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

    
            escalation = Escalation.objects.filter(id=data.get('id')).first()
            
            group = data.get('group_id')        
            user = get_user(request).id
            url = reverse('escalation', kwargs={'group_id': group, 'user_id': user})
            
            if not escalation:
                return JsonResponse({"error": "Escalation not found"}, status=404)
            
            
            if Escalation.objects.filter(group=group, name=data.get('name')).exists():
                return JsonResponse({"error": "Já existe uma escalação com esse nome.", "url": url}, status=409)

            escalation.name = data.get('name')
            escalation.position = data.get('position')
            escalation.phone = data.get('phone')
            escalation.email = data.get('email')
            escalation.area = data.get('area')
            escalation.service = data.get('service')
            escalation.level = data.get('level')
            escalation.save()
            
            
            return JsonResponse({"url": url}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)
       


