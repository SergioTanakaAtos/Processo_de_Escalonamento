from django.shortcuts import render

# Create your views here.
def initial_page(request):
    return render(request, 'escalation/initial_page.html')