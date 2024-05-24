from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from escalation.models import LogPermission
from escalation.models import Group
from django.contrib.auth import get_user 


def permissions(request):
    is_superuser = get_user(request).is_superuser
    
    if is_superuser:
        permissions = LogPermission.objects.filter(is_active=None)
        
    else:    
        permissions = LogPermission.objects.filter(user=get_user(request))
        
    return render(request, 'permission.html', {'permissions': permissions, 'admin': is_superuser})



def save_permission(request, group_id):
    user = get_user(request)
    group = Group.objects.filter(id=group_id).get()
    
    if LogPermission.objects.filter(user=user, group=group).exists():
         return redirect('permissions')
    else:
        permission = LogPermission(user=user, group=group, is_active=None)
        LogPermission.save(permission)
        return redirect('escalation')
    
    
def accepted_permission(request, permission_id):
    permission = LogPermission.objects.filter(id=permission_id).get()
    permission.is_active = True
    permission.save()
    return redirect('permissions')


    
def denied_permission(request, permission_id):
    permission = LogPermission.objects.filter(id=permission_id).get()
    permission.is_active = False
    permission.save()
    return redirect('permissions')


