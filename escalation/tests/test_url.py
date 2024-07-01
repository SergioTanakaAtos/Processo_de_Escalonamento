from django.test import SimpleTestCase
from django.urls import reverse, resolve
from escalation.views import initial_page, escalation, save_group, create_escalation, edit_group, update_escalation, load_data, used_checkbox

class TestUrls(SimpleTestCase):
    
    def test_url_initial_page(self):
        url = reverse('initial_page')
        self.assertEquals(resolve(url).func, initial_page)
    
    def test_url_escalation(self):
        url = reverse('escalation',  kwargs={'group_id': 1, 'user_id': 2})
        self.assertEquals(resolve(url).func, escalation)
    
    def test_url_save_group(self):
        url = reverse('save_group')
        self.assertEquals(resolve(url).func, save_group)
    
    def test_url_create(self):
        url = reverse('create_escalation',  kwargs={'group_id': 1})
        self.assertEquals(resolve(url).func, create_escalation)
    
    def test_url_edit_group(self):
        url = reverse('edit_group')
        self.assertEquals(resolve(url).func, edit_group)
        
    def test_url_update_escalation(self):
        url = reverse('update_escalation')
        self.assertEquals(resolve(url).func, update_escalation)
        
    def test_url_load_data(self):
        url = reverse('load_data')
        self.assertEquals(resolve(url).func, load_data)
        
    def test_url_is_used(self):
        url = reverse('is_used')
        self.assertEquals(resolve(url).func, used_checkbox)

