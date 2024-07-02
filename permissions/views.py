from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from escalation.models import LogPermission, UserGroupDefault, User
from escalation.models import Group
from django.contrib.auth import get_user 
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='login')
def permissions(request):
    is_superuser = get_user(request).is_staff
    user_permissions_pending = []

    if is_superuser:
        users = User.objects.filter(is_staff=False)
        for user in users:
            pending_permissions = LogPermission.objects.filter(status='pending', user_id=user.id)
            if pending_permissions.exists():
                per = list(pending_permissions)
                user_per = {
                    "id": user.id,
                    "name": user.username,
                    "per": per
                }
                user_permissions_pending.append(user_per)

    return render(request, 'permission.html', {'users': user_permissions_pending, 'admin': is_superuser})




@login_required(login_url='login')
def save_permission(request, group_id):
    if LogPermission.objects.filter(status__in=['desactivate', 'denied']).exists():
        try:
            permission = LogPermission.objects.get(user=get_user(request), group=group_id)
            permission.status = 'pending'
            permission.save()
            return redirect('initial_page')
        except LogPermission.DoesNotExist:
            return JsonResponse({'message': 'Objeto com o usuário e grupo especificados não encontrado'}, status=404)
    return JsonResponse({'message': 'Condição não satisfeita para atualizar a permissão'}, status=400)


@login_required(login_url='login')      
def action_permission(request, permission_id, action):
    permission = LogPermission.objects.filter(id=permission_id).get()
    try:
        user_group = UserGroupDefault.objects.get(group=permission.group, user=permission.user)
    except UserGroupDefault.DoesNotExist:
        user_group = UserGroupDefault.objects.create(group=permission.group, user=permission.user)
    
    user_group = UserGroupDefault.objects.filter(
            group=permission.group,
            user=permission.user
        ).get()

    if action == "accepted":
        permission.status = 'activate'
        msg_success = 'aceita'
    else:
        permission.status = 'denied'
        user_group.is_visualizer = False
        msg_success = 'negada'
        
    permission.save()
    user_group.save()
    messages.success(request, f'Permissão {msg_success} com sucesso')
    return redirect('permissions')

        


