from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from escalation.models import LogPermission
from django.contrib.auth.models import Group
from .registerForm import RegisterForm
def register(request):

    form = RegisterForm()
    groups = Group.objects.all()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            permission_groups = request.POST.getlist('permissions')[0].split(',')
            user = form.save()
            for group_id in permission_groups:
                group = Group.objects.get(id=group_id)
                LogPermission.objects.create(user=user, group=group,is_active=None)
            return redirect('login')
        return render(request, 'users/register.html', {'form': form, 'error': form.errors, 'groups': groups})
    return render(request, 'users/register.html', {'form': form, 'groups': groups})
 
def login_view(request):
    if request.method == 'POST':
        # email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["senha"]
        user = authenticate(request, username=username, password=password)
        # user = User.objects.filter(email=email,password=password).first()
        
            
        if user is not None:
            login(request, user)
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