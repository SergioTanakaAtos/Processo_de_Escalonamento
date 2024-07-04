from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from escalation.models import LogPermission, UserGroupDefault
from django.contrib.auth import get_user_model
import json


User = get_user_model()
    

class RegisterViewTest(TestCase):

    def setUp(self):
        self.url = reverse('register')
        self.group1 = Group.objects.create(name='Group1')
        self.group2 = Group.objects.create(name='Group2')

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIn('form', response.context)
        self.assertIn('groups', response.context)
        self.assertEqual(len(response.context['groups']), 2)

    def test_invalid_form(self):
        data = {
            'username': '',
            'password1': 'password',
            'password2': 'password',
            'permissions': '',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # Não redireciona
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertIn('form', response.context)
        self.assertIn('errors', response.context)
        self.assertIn('groups', response.context)
        self.assertFalse(User.objects.filter(username='').exists())
        
        
    def test_register_successfully(self):
        data = {
            'username': 'testuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'permissions': f'{self.group1.id},{self.group2.id}',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertEqual(LogPermission.objects.filter(user=user).count(), 2)


class LoginViewTest(TestCase):
    
    def setUp(self):
        self.url = reverse('login')
        self.initial_page_url = reverse('initial_page')
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        
    def test_request_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        
    def test_login_invalid(self):
        data = {
            'username': 'testuser',
            'senha': 'wrongpassword',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertIn('message', response.context)
        self.assertEqual(response.context['message'], 'Usuário ou senha inválidos')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
    def test_login_successful(self):
        data = {
            'username': 'testuser',
            'senha': '12345',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.initial_page_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

class LogoutViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.client.login(username='testuser', password='testpassword')

    def test_logout(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        response = self.client.get(self.login_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        
class GetUsersViewTest(TestCase):
    
    def setUp(self):
        self.superuser = User.objects.create_user(username='testuser', password='12345', is_superuser=True)
        self.user2 = User.objects.create_user(username='testuser2', password='12345', is_superuser=False)
        self.user3 = User.objects.create_user(username='testuser3', password='12345', is_superuser=False)
        self.url = reverse('management')
        
    def test_get_users(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/management.html')
        self.assertIn('users', response.context)
        users = response.context['users']
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['name'], 'testuser2')
        self.assertEqual(users[1]['name'], 'testuser3')
    
    
class GetUsersGroupsViewTest(TestCase):
    
    def setUp(self):
        self.superuser = User.objects.create_user(username='testuser', password='12345', is_superuser=True)
        self.user2 = User.objects.create_user(username='testuser2', password='12345', is_superuser=False)
        self.user3 = User.objects.create_user(username='testuser3', password='12345', is_superuser=False)
        self.url = reverse('management')
        
    def test_get_users(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/management.html')
        self.assertIn('users', response.context)
        users = response.context['users']
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]['name'], 'testuser2')
        self.assertEqual(users[1]['name'], 'testuser3')
           
           
class GetUserGroupsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_user(username='testsuperuser', password='12345', is_superuser=True)
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@atos.net', is_staff=False, is_superuser=False)
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')
        self.user_group_default1 = UserGroupDefault.objects.create(group=self.group1, user=self.user, is_visualizer=True)
        self.user_group_default2 = UserGroupDefault.objects.create(group=self.group2, user=self.user, is_visualizer=False)
        self.log_permission1 = LogPermission.objects.create(user=self.user, group=self.group1, status='activate')
        self.log_permission2 = LogPermission.objects.create(user=self.user, group=self.group2, status='denied')
        self.url = reverse('user_groups')
        
        
    def test_get_user_groups_no_id_provided(self):
        self.client.login(username='testsuperuser', password='12345')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], 'ID do usuário não fornecido')
        
    
    def test_get_user_groups_invalid_id(self):
        self.client.login(username='testsuperuser', password='12345')
        data = {'id': 'abc123'}
        response = self.client.get(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], 'Formato de ID de usuário inválido')
        
        
    def test_get_user_groups_user_not_found(self):
        self.client.login(username='testsuperuser', password='12345')
        data = {'id': 9999}  
        response = self.client.get(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        json_response = response.json()
        
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], 'Usuário não encontrado')
        
    def test_get_user_groups_success(self):
        self.client.login(username='testsuperuser', password='12345')
        data = {'id': self.user.id}
        response = self.client.get(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        self.assertIn('groups', json_response)
        self.assertIn('user', json_response)
        
        user_data = json_response['user']
        self.assertEqual(user_data['id'], self.user.id)
        self.assertEqual(user_data['username'], self.user.username)
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['is_staff'], self.user.is_staff)
        
        groups_data = json_response['groups']
        self.assertEqual(len(groups_data), 1)
        self.assertEqual(groups_data[0]['name'], 'Group 1')
        
        user_groups_default = UserGroupDefault.objects.filter(user=self.user)
        permissions = LogPermission.objects.filter(user=self.user)
        
        self.assertEqual(len(user_groups_default), 2)
        self.assertEqual(len(permissions), 2)
        
        self.assertTrue(user_groups_default[0].is_visualizer)
        self.assertFalse(user_groups_default[1].is_visualizer)
        self.assertEqual(permissions[0].status, 'activate')
        self.assertEqual(permissions[1].status, 'denied')
    
    
class UpdateUserGroupsViewTest(TestCase): 
    
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(username='superuser', password='12345')
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')
        self.log_permission = LogPermission.objects.create(user=self.user, group=self.group, status='activate')
        self.user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        self.url = reverse('update-user-groups')

    def test_update_user_groups_invalid_json(self):
        self.client.login(username='superuser', password='12345')
        response = self.client.post(self.url, 'invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON data"})

    def test_update_user_groups_staff_success(self):
        self.client.login(username='superuser', password='12345')
        data = {
            'id': self.user.id,
            'is_staff': True,
            'permissions': []
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        
        user_groups = UserGroupDefault.objects.filter(user=self.user.id)
        permisssions = LogPermission.objects.filter(user=self.user.id)

        self.assertEqual(permisssions[0].status, 'activate')
        self.assertTrue(user_groups[0].is_visualizer)
        self.assertEqual(response.json(), {"message": "Permissão alterada com sucesso"})
        

    def test_update_user_groups_with_permissions_success(self):
        self.client.login(username='superuser', password='12345')
        new_user = User.objects.create_user(username='newuser', password='12345')
        new_group = Group.objects.create(name='New Group')
        UserGroupDefault.objects.create(user=new_user, group=new_group, is_visualizer=True)
        LogPermission.objects.create(user=new_user, group=new_group, status='activate')

        data = {
            'id': self.user.id,
            'is_staff': False,
            'permissions': [{'user': new_user.id, 'group': new_group.id}]
        }
        
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Permissão alterada com sucesso"})

        log_permission = LogPermission.objects.get(user=new_user, group=new_group)
        user_group = UserGroupDefault.objects.get(user=new_user, group=new_group)
        self.assertEqual(log_permission.status, 'desactivate')
        self.assertFalse(user_group.is_visualizer)
        
        
 