from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from escalation.models import LogPermission, UserGroupDefault
from django.contrib.auth.models import Group
from .registerForm import RegisterForm
from django.views.decorators.csrf import csrf_exempt
import json



def register(request):
    form = RegisterForm()
    groups = Group.objects.all()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            permission_groups = request.POST.getlist('permissions')[0].split(',')
            user = form.save()
            if permission_groups == ['']:
                return redirect('login')
            for group_id in permission_groups:
                group = Group.objects.get(id=group_id)
                LogPermission.objects.create(user=user, group=group,status='pending')
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
        return render(request, 'users/login.html', {'message': 'Usuário ou senha inválidos'})
    return render(request, 'users/login.html')
 
def logout_view(request):
    logout(request)
    return redirect('login')
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
            permission_groups = LogPermission.objects.filter(user_id=id, status = 'activate').values_list('group', flat=True)
            groups = UserGroupDefault.objects.filter(group__in=permission_groups).values_list('group_id', flat=True)
            data = list(Group.objects.filter(id__in=groups).values('id', 'name'))

            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }

            print(data)
            return JsonResponse({'groups': data, 'user': user_data})
        except (ValueError, ObjectDoesNotExist):
            return JsonResponse({'error': 'User not found or invalid id'}, status=400)



@csrf_exempt
def update_user_groups(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            permissions = data  
       
            for p in permissions:
           
                user_group = UserGroupDefault.objects.filter(id=p['id']).get()
                # log_permission = LogPermission.objects.filter(user=user_group.group, group=user_group.group).get()
                print("Usuário:", user_group.user)  
                print("Grupos:", user_group.group)
                # log_permission.status = 'desactivate'
                # user_group.is_visualizer = False
                
                # log_permission.save()
                # print(log_permission)
                # print(user_group)


            return JsonResponse({"message": "Success"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

  

        #     return JsonResponse({'groups': data, 'user': user_data})
        # except (ValueError, ObjectDoesNotExist):
        #     return JsonResponse({'error': 'User not found or invalid id'}, status=400)