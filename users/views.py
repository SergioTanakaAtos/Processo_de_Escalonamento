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
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from escalation import signals

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
        errors = [error[0] for error in form.errors.values()]
        return render(request, 'users/register.html', {'form': form, 'errors': errors, 'groups': groups})
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


@login_required(login_url='login')
def get_users(request):
    users = User.objects.filter(is_superuser=False)
    users_for_management = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.username,
        }
        users_for_management.append(user_data)
   
    return render(request, 'users/management.html', {'users': users_for_management})
 


@login_required(login_url='login')
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
                'is_staff': user.is_staff
            }


            return JsonResponse({'groups': data, 'user': user_data})
        except (ValueError, ObjectDoesNotExist):
            return JsonResponse({'error': 'User not found or invalid id'}, status=404)



@login_required(login_url='login')
@csrf_exempt
def update_user_groups(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = User.objects.filter(id=data['id']).first()
            
            if not data['is_staff']:
                user.is_staff = False
                user.save()
            else:
                user.is_staff = True
                user.save()
                    
                permissions = LogPermission.objects.filter(user=user)
                permissions.exclude(status='activate').update(status='activate')
                    
                user_groups = UserGroupDefault.objects.filter(user=user)
                user_groups.filter(is_visualizer=False).update(is_visualizer=True)

                groups = Group.objects.all()
            
                for group in groups:
                    if not UserGroupDefault.objects.filter(user=user, group=group).exists():
                        UserGroupDefault.objects.create(user=user, group=group, is_visualizer=True)
                    if not LogPermission.objects.filter(user=user, group=group).exists():
                        LogPermission.objects.create(user=user, group=group, status='activate')     
       
            if len(data['permissions']) != 0:
                for p in data['permissions']:
                    group = Group.objects.filter(id=int(p['group'])).get()
                    user_per = User.objects.filter(id=int(p['user'])).get()
                    user_group = UserGroupDefault.objects.filter(user=user_per, group=group, is_visualizer=True).get()
                    log_permission = LogPermission.objects.filter(user=user_per, group=group).get()
                    
                    log_permission.status = 'desactivate'
                    user_group.is_visualizer = False

                    log_permission.save()
                    user_group.save()
                
            
            
  
            return JsonResponse({"message": "Permissão alterada com sucesso"}, status=200)    

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        
    

# def update_level_user(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             user = User.objects.filter(id=data.get('id')).first()
            
#             if user.is_staff == True:
#                 user.is_staff = False
#                 user.save()
            
#                 return JsonResponse({"message": "Usuário alterado com sucesso!"}, status=200)
            
            
#             user.is_staff = True
#             user.save()
            
#             permissions = LogPermission.objects.filter(user=user)
#             permissions.exclude(status='activate').update(status='activate')
             
#             user_groups = UserGroupDefault.objects.filter(user=user)
#             user_groups.filter(is_visualizer=False).update(is_visualizer=True)

#             groups = Group.objects.all()
            
#             for group in groups:
#                 if not UserGroupDefault.objects.filter(user=user, group=group).exists():
#                     UserGroupDefault.objects.create(user=user, group=group, is_visualizer=True)
#                 if not LogPermission.objects.filter(user=user, group=group).exists():
#                     LogPermission.objects.create(user=user, group=group, status='activate')

                
#             return JsonResponse({"message": "Usuário alterado com sucesso!"}, status=200)
        
#         except User.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)
