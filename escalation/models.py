from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User


class Escalation(models.Model):
    """
    Represents an escalation.
    """
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    level = models.IntegerField()
    area = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='escalations')

    def __str__(self):
        return str(self.name)

    class Meta:
        """
        Meta options for the Escalation model.
        """
        ordering = ['level']

class UserGroupDefault(models.Model):
    is_visualizer = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='usergroupdefaults')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usergroupdefaults')

class UserEscalationIsUsed(models.Model):
    escalation = models.ForeignKey(Escalation, on_delete=models.CASCADE, related_name='userescalationisused')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userescalationisused')
    date = models.DateTimeField()

class LogPermission(models.Model):
    STATUS_CHOICES = [
        ('activate', 'Activate'),
        ('desactivate', 'Desactivate'),
        ('denied', 'Denied'),
        ('pending', 'Pending'),
    ]
 
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default='desactivate',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='log_permissions')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='log_permissions')
    created_at = models.DateTimeField(auto_now_add=True)