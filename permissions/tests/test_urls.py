from django.urls import reverse, resolve
from permissions.views import permissions, save_permission, action_permission
from django.test import SimpleTestCase


class TestPermissionsUrls(SimpleTestCase):
    def test_permissions_url_resolves(self):
        url = reverse('permissions')
        self.assertEqual(resolve(url).func, permissions)

    def test_create_permission_url_resolves(self):
        url = reverse('create-permission', args=[1])
        self.assertEqual(resolve(url).func, save_permission)

    def test_action_permission_url_resolves(self):
        url = reverse('action-permission', args=['accepted', 1])
        self.assertEqual(resolve(url).func, action_permission)