from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Escalation
from .models import UserGroupDefault
from .models import LogPermission
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test

from django.http import HttpResponseForbidden
from django.http import JsonResponse    
import os
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
# Create your views here.

from collections import defaultdict
from django.shortcuts import render
from .models import Escalation
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import graphviz
from collections import defaultdict

def initial_page(request):
    #pylint: disable=E1101
    groups = Group.objects.all()
    user = request.user
    group_states = {} 
    states_mapping = {None: "Permissão pendente", True: "Permitido", False: "Não pediu permissão"}

    for group in groups:
        log_per, created = LogPermission.objects.get_or_create(group=group, user=user)
        user_group = UserGroupDefault.objects.filter(group=group, user=user).first()
        if user_group.is_visualizer:
            log_per.is_active = True
        if created:
            log_per.save()

        group_states[group] = states_mapping.get(log_per.is_active, "Não pediu permissão")
    return render(request, 'escalation/initial_page.html', {'group_states': group_states})

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def save_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            group_name_lower = group_name.lower()
            if Group.objects.filter(name__iexact=group_name_lower).exists():
                return JsonResponse({'message':'O nome do grupo já existe.'}, status=400)
            group = Group(name=group_name)
            group.save()
            return JsonResponse({'message':'Grupo criado com sucesso.'}, status=200)
        else:
            return JsonResponse({'message':'O nome do grupo não pode estar vazio.'}, status=400)
    return JsonResponse({'message':'Método não permitido.'}, status=405)
@csrf_exempt
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def edit_group(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        new_group_name = request.POST.get('new_company')
        group = Group.objects.get(id=group_id)
        group.name = new_group_name
        group.save()
        return JsonResponse({'message':'Grupo criado com sucesso.'}, status=200)
    
    return render(request, 'initial_page.html')     

@csrf_exempt
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def load_data(request):
    if request.method == 'POST' and request.FILES['xlsx_file']:
        xlsx_file = request.FILES['xlsx_file']
        
        upload_dir = os.path.join(settings.BASE_DIR, 'escalation/data')
                
        os.makedirs(upload_dir, exist_ok=True)
        
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(xlsx_file.name, xlsx_file)
        
        file_path = fs.path(filename)
        df = pd.read_excel(file_path,engine='openpyxl')
        for index, row in df.iterrows():
            group_name = row['Empresa'].replace(' ', '')
            group, created = Group.objects.get_or_create(name=group_name)
            name = row['Nome'].replace(' ', '')
            position = row['Cargo']
            phone = row['Telefone'] if not pd.isnull(row['Telefone']) else ''
            email = row['Email']
            level = row['Nível']
            area = row['Área']
            service = row['Serviço']
            #pylint: disable=E1101
            if not Escalation.objects.filter(name=name, group=group).exists():
                escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
                escalation.save()
        return redirect('initial_page')    
def escalation(request, group_id, user_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    
    user_group_default = get_object_or_404(UserGroupDefault, user=user, group=group)

    if not user_group_default.is_visualizer:
        return HttpResponseForbidden("Você não tem permissão para visualizar este cliente.")
    

    escalation = Escalation.objects.filter(group=group)
    escalation_tree()
    if not escalation:
        return render(request, 'escalation/escalation_page.html', {'group': group, 'message': "Não há escalonamento cadastrado para este grupo."})
    return render(request, 'escalation/escalation_page.html', {'group': group, 'escalation': escalation})



def create_escalation(request, group_id):
    #pylint: disable=E1101
    group = Group.objects.get(id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if Escalation.objects.filter(group=group, name=name).exists():
            return render(request,'escalation/create_escalation.html', {'group': group, 'message': 'Já existe um escalonamento com este nome.'})
        else:
            position = request.POST.get('position')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            area = request.POST.get('area')
            service = request.POST.get('service')
            level = request.POST.get('level')
            escalation = Escalation(name=name, position=position, phone=phone, email=email, level=level, area=area, service=service, group=group)
            
            escalation.save()
        
            return render(request, 'escalation/create_escalation.html', {'group': group})
    return render(request, 'escalation/create_escalation.html', {'group': group})



def escalation_tree():
    # pylint: disable=E1101\w
    escalation = Escalation.objects.order_by('level')
    tree = defaultdict(list)
    for esc in escalation:
        tree[esc.level].append(esc.name)

    # Convertendo o defaultdict para um dicionário normal
    tree = dict(tree)
    print(tree)

    # Construindo a árvore com anytree
    root = Node("Escalation")

    # Dicionário para armazenar os nós por nível
    nodes = {0: root}
    for level in sorted(tree.keys()):
        for name in tree[level]:
            # Cada nó é filho do nível anterior
            parent = nodes[level - 1]
            nodes[level] = Node(name, parent=parent)

    # Exportando a árvore para um arquivo DOT
    DotExporter(root).to_dotfile("tree.dot")

    # Convertendo o arquivo DOT para um gráfico SVG usando graphviz
    with open("tree.dot") as f:
        dot_graph = f.read()
    graph = graphviz.Source(dot_graph)
    graph.render("tree", format="svg", cleanup=True)

    # Gerar o conteúdo HTML para visualizar a árvore
    html_content = """

        <h1>Escalation Tree Visualization</h1>
        <img src="/static/tree.svg" alt="Tree Visualization">
    </body>
    </html>
    """

    # Salvando o HTML em um arquivo
    with open("templates/tree.html", "w") as file:
        file.write(html_content)

    return "tree.html"

def tree_view(request):
    html_file = escalation_tree()
    return render(request, html_file)
