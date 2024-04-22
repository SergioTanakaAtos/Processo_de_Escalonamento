from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Escalation(models.Model):
    """
    Represents an escalation.
    """
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField()
    level = models.IntegerField()
    area = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='escalations')

    def __str__(self):
        return str(self.name)

    class Meta:
        """
        Meta options for the Escalation model.
        """
        ordering = ['level']

class UserGroupDefault(models.Model):
    is_visualizer = models.BooleanField(default=False)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='usergroupdefaults')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usergroupdefaults')
    def save(self, *args, **kwargs):
        user = User.objects.get(id=self.user_id)
        if user.is_superuser or user.is_staff:
            self.is_visualizer = True
        super().save(*args, **kwargs)
class Log_permission(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='log_permissions')
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='log_permissions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)