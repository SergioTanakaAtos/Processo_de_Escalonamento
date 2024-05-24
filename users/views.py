from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from escalation.models import LogPermission
from django.contrib.auth.models import Group
from .registerForm import RegisterForm
def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form)
        if form.is_valid():

            # form.save()
            # user = User.objects.get(name=)
            # for group in form.cleaned_data['permissions']:
            #     LogPermission.objects.create(user=user, group=group)
            return redirect('initial_page')
        """

        Relacionamento

        Instanciar a tebala logpermission com o id das permissoes juntamente com o novo id user e setar o is_active como null(não nessesariamente é aqui que se faz isso, ver melhor depois)
        
        Instaciar a tabela usergroupdefault com o id do grupo e o id do user para criar esse relacionamento False
        is_active -

            False: não pediu permissão

            null: Permissão pendente

            True: Permitido

        |

        |

        V verificar se está certo a maneira de salvar o nome.

        """    
    return render(request, 'users/register.html', {'form': form})
 
def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["senha"]
        user = authenticate(request, email=email, password=password)
        print(f"user = {user}, email = {email}, senha = {password}")
        if user is not None:
           # login(request, user)
            return redirect('initial_page')
        return render(request, 'users/login.html', {'error': 'Usuário ou senha inválidos'})
    return render(request, 'users/login.html')
 
def logout(request):
    logout(request)
    return redirect('')

def get_users(request):
    users = User.objects.all()
    users_for_management = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.username,
        }
        users_for_management.append(user_data)
   
    return render(request, 'users/management.html', {'users': users_for_management})
 
 
def get_user_groups(request):
    if request.method == "GET":
        id = int(request.GET.get('id'))
        groups_ids = LogPermission.objects.filter(user_id=id).values_list('group_id', flat=True)
        groups = Group.objects.filter(id__in=groups_ids)
        data = list(groups.values('id', 'name'))
        return JsonResponse({'groups': data})