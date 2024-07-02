from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission, Escalation, UserGroupDefault, UserEscalationIsUsed
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import os
from io import BytesIO
import os
import django
import json

os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()

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
        response = self.client.get(self.url, follow=True)
        self.assertIsNotNone(response.context)
        self.assertIn('group_states', response.context)

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


class SaveGroupViewTests(TestCase):
    
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


class EditGroupViewTests(TestCase):
    
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
        self.assertEqual(response.status_code, 405)  

        
    def test_group_name_empty(self):
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
        

class LoadDataViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_staff = User.objects.create_user(username='staffuser', password='12345', is_staff=True, is_superuser=True)
        self.url = reverse('load_data')
        
        
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")  
    
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
        
        
class EscalationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        
    def test_user_not_in_group(self):
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f'Usuário não tem permissão no(a) {self.group.name}. Contate o administrador.', messages)
        self.assertRedirects(response, reverse('initial_page'))

    def test_user_not_visualizer(self):
        UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=False)
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f'Usuário não tem permissão no(a) {self.group.name}. Contate o administrador.', messages)
        self.assertRedirects(response, reverse('initial_page'))

    def test_no_escalation_for_group(self):
        UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Não há escalonamento cadastrado para este grupo.', messages)
        self.assertEqual(response.status_code, 200) 

    def test_escalation_exists(self):
        UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        Escalation.objects.create(name='Test Name', group=self.group, level=1)  
        url = reverse('escalation', args=(self.group.id, self.user.id))
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertContains(response, 'Test Name') 
        self.assertEqual(response.status_code, 200)


class CreateEscalationViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')  
        self.group = Group.objects.create(name='Test Group')
        self.escalation = Escalation.objects.create(name='Melissa', level=1, group=self.group)
    
    def test_method_get(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('create_escalation', kwargs={'group_id': self.group.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'escalation/create_escalation.html')
    
    
    def test_empty_fields(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('create_escalation', kwargs={'group_id': self.group.id})
        response = self.client.post(url, {'name_new_escalation': 'Melissa', 'position': '', 'phone': '', 'email': 'melissa@atos.net', 'area': 'DWP', 'service': '', 'level': ''})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Preencha todos os campos necessários', messages)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'escalation/create_escalation.html')
        
    
    def test_empty_fields(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('create_escalation', kwargs={'group_id': self.group.id})
        response = self.client.post(url, {'name': 'Melissa', 'position': '', 'phone': '', 'email': 'melissa@atos.net', 'area': 'DWP', 'service': '', 'level': ''})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Preencha todos os campos necessários', messages)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'escalation/create_escalation.html')
        
    def test_name_group_alredy_exist(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('create_escalation', kwargs={'group_id': self.group.id})
        response = self.client.post(url, {'name_new_escalation': 'Melissa', 'position': 'Estag', 'phone': '1111', 'email': 'melissa@atos.net', 'area': 'DWP', 'service': 'Dev', 'level': 1})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Já existe um escalonamento com este nome.', messages)
        self.assertEqual(response.status_code, 409)
        self.assertTemplateUsed(response, 'escalation/create_escalation.html')
        
    def test_created_successful(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('create_escalation', kwargs={'group_id': self.group.id})
        response = self.client.post(url, {
            'name_new_escalation': 'Melissa Neves', 
            'position': 'Estag', 
            'phone': '222222', 
            'email': 'melissa@atos.net', 
            'area': 'DWP', 
            'service': 'Dev', 
            'level': 1
        }, follow=True)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Escalonamento criado com sucesso.', messages)

        expected_url = reverse('escalation', kwargs={'group_id': self.group.id, 'user_id': self.user.id})
        final_response = self.client.get(expected_url)
        self.assertEqual(final_response.status_code, 302)
        self.assertTrue(Escalation.objects.filter(name='Melissa Neves').exists())
        
        
class UpdateEscalationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        self.escalation = Escalation.objects.create(name='Initial Name', level=1, group=self.group)
        self.client.login(username='testuser', password='12345')
        self.url = reverse('update_escalation')

    def test_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Invalid method"})

    def test_invalid_json(self):
        response = self.client.post(self.url, "Invalid JSON", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid JSON"})

    def test_escalation_not_found(self):
        data = json.dumps({'id': 9999, 'name': 'Nonexistent Escalation', 'group_id': self.group.id})
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"error": "Escalonamento não encontrado"})

    def test_duplicate_escalation_name(self):
        Escalation.objects.create(name='Duplicate Name', level=2, group=self.group)
        data = {
            'id': self.escalation.id, 
            'name': 'Duplicate Name', 
            'level': 2,
            'group_id': self.group.id
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 409)
        expected_url = reverse('escalation', kwargs={'group_id': self.group.id, 'user_id': self.user.id})
        self.assertJSONEqual(response.content, {"error": "Já existe um escalonamento com esse nome.", "url": expected_url})

    def test_successful_update(self):
        data = {
            'id': self.escalation.id, 
            'name': 'Updated Name', 
            'position': 'Updated Position', 
            'phone': '222222', 
            'email': 'updated@domain.com', 
            'area': 'Updated Area', 
            'service': 'Updated Service', 
            'level': 2,
            'group_id': self.group.id
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        expected_url = reverse('escalation', kwargs={'group_id': self.group.id, 'user_id': self.user.id})
        self.assertJSONEqual(response.content, {"url": expected_url})
        self.escalation.refresh_from_db()
        self.assertEqual(self.escalation.name, 'Updated Name')
        self.assertEqual(self.escalation.position, 'Updated Position')
        self.assertEqual(self.escalation.phone, '222222')
        self.assertEqual(self.escalation.email, 'updated@domain.com')
        self.assertEqual(self.escalation.area, 'Updated Area')
        self.assertEqual(self.escalation.service, 'Updated Service')
        self.assertEqual(self.escalation.level, 2)        


class UsedCheckboxViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        self.escalation = Escalation.objects.create(name='Test Escalation', level=1, group=self.group)
        self.client.login(username='testuser', password='12345')
        self.url = reverse('is_used')

    def test_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_invalid_json(self):
        response = self.client.post(self.url, "Invalid JSON", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Invalid JSON"})

    def test_successful_update(self):
        data = {
            'is_used': True,
            'escalation_id': self.escalation.id
        }
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())
        self.assertIn("datetime", response.json())
        self.assertTrue(UserEscalationIsUsed.objects.filter(escalation=self.escalation, user=self.user).exists())


      
        
        
        
    
      
    
    
        