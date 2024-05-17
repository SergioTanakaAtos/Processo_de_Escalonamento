from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission

# Create your views here.
def index(request):
    return render(request, 'users/index.html')

def register(request):
    return render(request, 'users/cadastro.html')

def get_users(request):
    users = User.objects.all()

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
        }
        users_for_management.append(user_data)
    
    return render(request, 'users/management.html', {'users': users_for_management})



def cadastro_exemplo(request):
    user = User.objects.create_user("teste", "lennon@thebeatles.com", "johnpassword")
    user.set_username = "Lennon"
    user.save()
    return HttpResponse("Usuário salvo com sucesso!")