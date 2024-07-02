# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from escalation.models import LogPermission, UserGroupDefault, Group
from django.contrib.messages import get_messages

User = get_user_model()

class TestPermissionsViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
        self.user = User.objects.create_user(username='user', password='userpass')
        self.group = Group.objects.create(name='Test Group')
        self.permission = LogPermission.objects.create(user=self.user, group=self.group, status='pending')

    def test_permissions_view_as_superuser(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('permissions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permission.html')
        self.assertIn('users', response.context)
        self.assertTrue(response.context['admin'])
        

    def test_permissions_view_as_non_superuser(self):
        self.client.login(username='user', password='userpass')
        response = self.client.get(reverse('permissions'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'permission.html')
        self.assertFalse(response.context['admin'])

    def test_save_permission_view(self):
        self.permission.status = 'desactivate'
        self.permission.save()
        
        self.client.login(username='user', password='userpass')
        response = self.client.post(reverse('create-permission', args=[self.group.id]))
        self.assertRedirects(response, reverse('initial_page'))
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.status, 'pending')

    def test_action_permission_view_accepted(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('action-permission', args=['accepted',self.permission.id]))
        self.assertRedirects(response, reverse('permissions'))
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.status, 'activate')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Permissão aceita com sucesso')

    def test_action_permission_view_denied(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('action-permission', args=['denied',self.permission.id]))
        self.assertRedirects(response, reverse('permissions'))
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.status, 'denied')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Permissão negada com sucesso')
