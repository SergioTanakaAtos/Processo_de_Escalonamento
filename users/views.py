from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission

# Create your views here.
def index(request):
    return render(request, 'users/index.html')

def register(request):
    return render(request, 'users/cadastro.html')

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


def cadastro_exemplo(request):
    user = User.objects.create_user("teste", "lennon@thebeatles.com", "johnpassword")
    user.set_username = "Lennon"
    user.save()
    return HttpResponse("Usuário salvo com sucesso!")