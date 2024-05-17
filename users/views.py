from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'users/index.html')

def register(request):
    return render(request, 'users/cadastro.html')

def get_users(request):
    user = User.objects.all()
    return render(request, 'users/management.html', {'users': user})

def cadastro_exemplo(request):
    user = User.objects.create_user("teste", "lennon@thebeatles.com", "johnpassword")
    user.set_username = "Lennon"
    user.save()
    return HttpResponse("Usuário salvo com sucesso!")