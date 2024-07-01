from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission, Escalation, UserGroupDefault
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import os
from io import BytesIO
from escalation.views import escalation 

class InitialPageViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        groups = [
            Group.objects.create(name='Group 1'),
            Group.objects.create(name='Group 2'),
            Group.objects.create(name='Group 3')
        ]
        users = [  
            {'user': User.objects.create_user(username='staffuser', password='12345', is_staff=True, is_superuser=True), 'log_per': []},
            {'user': User.objects.create_user(username='normaluser', password='12345', is_staff=False, is_superuser=False), 'log_per': []}
        ]
        
        for user_dict in users:
            user = user_dict['user']
            for group in groups:
                if user.is_staff:
                    log_per = LogPermission.objects.create(group=group, user=user, status='activate')
                    user_dict['log_per'].append(log_per)

                else:
                    log_per = LogPermission.objects.create(group=group, user=user, status='pending')
                    user_dict['log_per'].append(log_per)

        self.groups = groups
        self.users = users
        self.url = reverse('initial_page')
        
        
    def test_template_used(self):
        self.client.login(username='normaluser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'escalation/initial_page.html')
        
    
    def test_initial_page_view_normal_user(self):
        self.client.login(username='normaluser', password='12345')
        response = self.client.get(self.url)
        group_states = response.context['group_states']
        
        for per in self.users[1].get('log_per'):
            self.assertEqual(per.status, "pending")
        
        for group in self.groups:
            self.assertIn(group, group_states)
            self.assertEqual(group_states[group], "Permissão pendente")
            
    
    def test_initial_page_view_staff_user(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.get(self.url)
        group_states = response.context['group_states']
        
        for group in self.groups:
            self.assertIn(group, group_states)
            self.assertEqual(group_states[group], "Permitido")
        
        for per in self.users[0].get('log_per'):
            self.assertEqual(per.status, "activate")
            
    
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class SaveGroupTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_user(username='superuser', password='12345', is_staff=True, is_superuser=True)
        self.staff_user = User.objects.create_user(username='staffuser', password='12345', is_staff=True, is_superuser=False)
        self.normal_user = User.objects.create_user(username='normaluser', password='12345', is_staff=False, is_superuser=False)
        
        self.url = reverse('save_group') 

        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")    
    
    
    def test_method_not_allowed(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Método não permitido.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 400)

    def test_group_empty(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.post(self.url, {'group_name': ''})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('O nome do grupo não pode ser vazio.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 400)
        
    def test_group_name_alredy_exists(self):
        self.client.login(username='staffuser', password='12345')
        Group.objects.create(name='Test Group')
        response = self.client.post(self.url, {'group_name': 'Test Group'})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Já existe um grupo com este nome.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 409)
        
    
    def test_group_created_successfully(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.post(self.url, {'group_name': 'Test Group'})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Grupo criado com sucesso.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Group.objects.filter(name='Test Group').exists())


class EditGroupTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staffuser', password='12345', is_staff=True, is_superuser=False)
        self.url = reverse('edit_group') 
        self.group = Group.objects.create(name='Test Group')
        
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")  
        
    
    def test_method_not_allowed(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Método não permitido.', [msg.message for msg in messages])
        self.assertTemplateUsed(response, 'escalation/initial_page.html')
        self.assertEqual(response.status_code, 403)
        
        
    def test_grou_name_empty(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.post(self.url, {'new_company': '', 'group_id': self.group.id})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('O nome do grupo não pode ser vazio.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 400)
        
        
    def test_group_created_successfully(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.post(self.url, {'new_company': 'New Group Name', 'group_id': self.group.id})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Grupo editado com sucesso.', [msg.message for msg in messages])
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'New Group Name')
        

class LoadDataTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_staff = User.objects.create_user(username='staffuser', password='12345', is_staff=True, is_superuser=True)
        self.url = reverse('load_data')
    
    def test_method_not_allowed(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Método HTTP não suportado.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 302)

    def test_upload_no_file(self):
        self.client.login(username='staffuser', password='12345')
        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Nenhum arquivo XLSX foi enviado.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 302)

    def test_upload_empty_file(self):
        self.client.login(username='staffuser', password='12345')
        empty_df = pd.DataFrame()
        xlsx_io = BytesIO()
        empty_df.to_excel(xlsx_io, index=False)
        xlsx_io.seek(0)
        empty_xlsx = SimpleUploadedFile("empty.xlsx", xlsx_io.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        response = self.client.post(self.url, {'xlsx_file': empty_xlsx})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('O arquivo XLSX está vazio.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 302)

    def test_upload_successful(self):
        self.client.login(username='staffuser', password='12345')

        data = {
            'Empresa': ['Empresa1', 'Empresa2'],
            'Nome': ['Nome1', 'Nome2'],
            'Cargo': ['Cargo1', 'Cargo2'],
            'Telefone': ['Telefone1', 'Telefone2'],
            'Email': ['email1@example.com', 'email2@example.com'],
            'Nível': [1, 2],
            'Área': ['Área1', 'Área2'],
            'Serviço': ['Serviço1', 'Serviço2']
        }
        df = pd.DataFrame(data)
    
        xlsx_io = BytesIO()
        df.to_excel(xlsx_io, index=False)
        xlsx_io.seek(0)  
        xlsx_file = SimpleUploadedFile("test.xlsx", xlsx_io.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        response = self.client.post(self.url, {'xlsx_file': xlsx_file})
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Dados carregados com sucesso.', [msg.message for msg in messages])
        self.assertEqual(response.status_code, 302)

        self.assertTrue(Group.objects.filter(name='Empresa1').exists())
        self.assertTrue(Group.objects.filter(name='Empresa2').exists())
        self.assertTrue(Escalation.objects.filter(name='Nome1').exists())
        self.assertTrue(Escalation.objects.filter(name='Nome2').exists())
        
        
class EscalationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')

    def test_user_not_in_group(self):
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Usuário não pertence a este grupo.', messages)
        self.assertRedirects(response, reverse('initial_page'))

    def test_user_not_visualizer(self):
        user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=False)
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Usuário não tem permissão.', messages)
        self.assertRedirects(response, reverse('initial_page'))

    def test_no_escalation_for_group(self):
        user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Não há escalonamento cadastrado para este grupo.', messages)
        self.assertEqual(response.status_code, 200) 

    def test_escalation_exists(self):
        user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        Escalation.objects.create(name='Test Name', group=self.group, level=1)  
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertContains(response, 'Test Name') 
        self.assertEqual(response.status_code, 200)

    
        
        
        
        
    
      
    
    
        