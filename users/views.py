from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def index(request):
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
