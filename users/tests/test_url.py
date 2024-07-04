from django.urls import reverse, resolve
from users.views import register, login_view, logout_view, get_user_groups,get_users, update_user_groups
from django.test import SimpleTestCase


class TestUsersUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, register)

    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, login_view)
        
    def test_logout_url_resolves(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_view)
        
    def test_user_groups_url_resolves(self):
        url = reverse('user_groups')
        self.assertEqual(resolve(url).func, get_user_groups)
        
    def test_get_users_url_resolves(self):
        url = reverse('management')
        self.assertEqual(resolve(url).func, get_users)
        
    def test_update_user_groups_url_resolves(self):
        url = reverse('update-user-groups')
        self.assertEqual(resolve(url).func, update_user_groups)

