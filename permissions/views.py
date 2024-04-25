from django.shortcuts import render
from django.http import HttpResponse



def permissions(request):
    return render(request, 'permission.html')
