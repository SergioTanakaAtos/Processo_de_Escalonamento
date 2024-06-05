from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from escalation.models import LogPermission
from escalation.models import Group
from django.contrib.auth import get_user 


def permissions(request):
    is_superuser = get_user(request).is_superuser
    if is_superuser:
        permissions = LogPermission.objects.filter(status='pending')
        
    else:    
        permissions = LogPermission.objects.filter(user=get_user(request))
   
    return render(request, 'permission.html', {'permissions': permissions, 'admin': is_superuser})



def save_permission(request, group_id):
 
    if LogPermission.objects.filter(status='desactivate'):
        try: 
            permission = LogPermission.objects.filter(user=get_user(request), group=group_id).get()
            permission.status = 'pending'
            permission.save()
            return redirect('permissions')
        except LogPermission.DoesNotExist:
            return JsonResponse({'message':'Objeto com o usuário e grupo especificados não encontrado'}, status=404)

        
def accepted_permission(request, permission_id):
    permission = LogPermission.objects.filter(id=permission_id).get()
    permission.status = 'activate'
    permission.save()
    return redirect('permissions')


    
def denied_permission(request, permission_id):
    permission = LogPermission.objects.filter(id=permission_id).get()
    permission.status = 'denied'
    permission.save()
    return redirect('permissions')


