import django
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'app.settings'
django.setup()


from django.test import TestCase
from escalation.models import Escalation, Group, UserGroupDefault, UserEscalationIsUsed, UserEscalationIsUsed, LogPermission
from datetime import datetime
from django.contrib.auth.models import User, Group
from django.utils.timezone import make_aware
from django.conf import settings

class EscalationTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name="Test Group")

        self.escalation = Escalation.objects.create(
            name="Melissa Neves",
            position="Operations Manager",
            phone="11 99999-9999",
            email="melissa.neves@example.com",
            level=2,
            area="DWP-Global Onsite Services",
            service="GOSS",
            group=self.group
        )

    def test_escalation_creation(self):
        self.assertEqual(self.escalation.name, "Melissa Neves")
        self.assertEqual(self.escalation.position, "Operations Manager")
        self.assertEqual(self.escalation.phone, "11 99999-9999")
        self.assertEqual(self.escalation.email, "melissa.neves@example.com")
        self.assertEqual(self.escalation.level, 2)
        self.assertEqual(self.escalation.area, "DWP-Global Onsite Services")
        self.assertEqual(self.escalation.service, "GOSS")
        self.assertEqual(self.escalation.group, self.group)

        
class UserGroupDefaultTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')

    def test_usergroupdefault_creation(self):
        user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        self.assertEqual(user_group_default.user, self.user)
        self.assertEqual(user_group_default.group, self.group)
        self.assertTrue(user_group_default.is_visualizer)

    def test_usergroupdefault_related_names(self):
        user_group_default = UserGroupDefault.objects.create(user=self.user, group=self.group, is_visualizer=True)
        self.assertIn(user_group_default, self.user.usergroupdefaults.all())
        self.assertIn(user_group_default, self.group.usergroupdefaults.all())


class UserEscalationIsUsedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Group Test')
        self.escalation = Escalation.objects.create(name='Test Escalation', level=1, group=self.group)

    def test_userescalationisused_creation(self):
        naive_datetime = datetime.now()
        now = make_aware(naive_datetime)
        user_escalation_used = UserEscalationIsUsed.objects.create(user=self.user, escalation=self.escalation, date=now)
        self.assertEqual(user_escalation_used.user, self.user)
        self.assertEqual(user_escalation_used.escalation, self.escalation)
        self.assertEqual(user_escalation_used.date, now)

    def test_userescalationisused_related_names(self):
        date = datetime.now()
        user_escalation_used = UserEscalationIsUsed.objects.create(user=self.user, escalation=self.escalation, date=make_aware(date))
        self.assertIn(user_escalation_used, self.user.userescalationisused.all())
        self.assertIn(user_escalation_used, self.escalation.userescalationisused.all())
        
        
class LogPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='Test Group')

    def test_logpermission_creation(self):
        log_permission = LogPermission.objects.create(user=self.user, group=self.group, status='activate')
        self.assertEqual(log_permission.user, self.user)
        self.assertEqual(log_permission.group, self.group)
        self.assertEqual(log_permission.status, 'activate')

    def test_logpermission_created_at(self):
        log_permission = LogPermission.objects.create(user=self.user, group=self.group, status='pending')
        self.assertIsNotNone(log_permission.created_at)

    def test_logpermission_related_names(self):
        log_permission = LogPermission.objects.create(user=self.user, group=self.group, status='activate')
        self.assertIn(log_permission, self.user.log_permissions.all())
        self.assertIn(log_permission, self.group.log_permissions.all())