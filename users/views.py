<<<<<<< HEAD
<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
=======
from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission
>>>>>>> 794d11a486a6c769dfa4245ccfec4cbf7ed6363c
=======
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission
>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43

def index(request):
<<<<<<< HEAD
<<<<<<< HEAD
    return render(request, 'users/login.html')


def register(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        permissoes = request.POST.getlist('permissao')
        confirmar_senha = request.POST.get('confirmarSenha')

        if not email.endswith('@atos.net'): 
            return render(request, 'users/register.html', {'error': 'O e-mail fornecido não é válido'})
        user = User.objects.create_user(usuario, email, senha)
        user.save()
        return render(request, 'users/login.html')
    else:
        return render(request, 'users/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["senha"]
        user = authenticate(request, email=email, password=password)
        print(f"user = {user}, email = {email}, senha = {password}")
        if user is not None:
           # login(request, user)
            return redirect('initial_page')
        else:
            return render(request, 'users/login.html', {'error': 'Usuário ou senha inválidos'})
    return render(request, 'users/login.html')

def logout(request):
    logout(request)
    return redirect('')
=======
=======
>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43
    return render(request, 'users/index.html')

def register(request):
    return render(request, 'users/cadastro.html')

def get_users(request):
    users = User.objects.all()
<<<<<<< HEAD

    def get_groups(user_id):
        # Obtem os IDs dos grupos associados ao usuário
        groups_ids = LogPermission.objects.filter(user_id=user_id).values_list('group_id', flat=True)
        # Obtem os grupos baseados nos IDs
        groups = Group.objects.filter(id__in=groups_ids)
        return groups


    users_for_management = []
    for user in users:
        user_data = {
            'name': user.username,
            'groups': get_groups(user.id)
=======
    users_for_management = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.username,
>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43
        }
        users_for_management.append(user_data)
    
    return render(request, 'users/management.html', {'users': users_for_management})


<<<<<<< HEAD
=======
def get_user_groups(request):
    if request.method == "GET":
        id = int(request.GET.get('id'))
        groups_ids = LogPermission.objects.filter(user_id=id).values_list('group_id', flat=True)
        groups = Group.objects.filter(id__in=groups_ids)
        data = list(groups.values('id', 'name'))
        return JsonResponse({'groups': data})

>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43

def cadastro_exemplo(request):
    user = User.objects.create_user("teste", "lennon@thebeatles.com", "johnpassword")
    user.set_username = "Lennon"
    user.save()
<<<<<<< HEAD
    return HttpResponse("Usuário salvo com sucesso!")
>>>>>>> 794d11a486a6c769dfa4245ccfec4cbf7ed6363c
=======
    return HttpResponse("Usuário salvo com sucesso!")
>>>>>>> df6083bf91c7866ff210afcd4222c495bfbb7d43
