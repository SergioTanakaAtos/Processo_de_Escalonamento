from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from escalation.models import LogPermission
from django.contrib.auth.models import Group

 
def register(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        permissoes = request.POST.getlist('permissao')
        confirmar_senha = request.POST.get('confirmarSenha')
 
        if senha != confirmar_senha:
            return render(request, 'users/register.html', {'error': 'As senhas não coincidem!'})
 
        if not email.endswith('@atos.net'):
           return render(request, 'users/register.html', {'error': 'O e-mail fornecido não é válido'})
        user = User.objects.create_user(usuario, email, senha)
        user.save()
        return render(request, 'users/login.html')
    
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
        try:
            id = int(request.GET.get('id'))
            user = User.objects.get(id=id)
            groups_ids = LogPermission.objects.filter(user_id=id).values_list('group_id', flat=True)
            groups = Group.objects.filter(id__in=groups_ids)
            data = list(groups.values('id', 'name'))

            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }

            return JsonResponse({'groups': data, 'user': user_data})
        except (ValueError, ObjectDoesNotExist):
            return JsonResponse({'error': 'User not found or invalid id'}, status=400)


