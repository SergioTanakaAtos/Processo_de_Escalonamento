from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import UserGroupDefault

@receiver(post_save, sender=User)
def update_usergroup_default(sender, instance, created, **kwargs):
    #pylint: disable=E1101
    """
    Atualiza o campo is_visualizer em UserGroupDefault
    sempre que um novo usuário é criado.
    """
    if created:
        if instance.is_superuser or instance.is_staff:
            for group in Group.objects.all():
                UserGroupDefault.objects.create(user=instance, is_visualizer=True, group=group)
                
def update_existing_superusers_and_staff(sender, instance, created, **kwargs):
    #pylint: disable=E1101
    """
    Atualiza o campo is_visualizer em UserGroupDefault
    para todos os superusuários e staff existentes
    quando um novo grupo é criado.
    """
    if created:
        superusers_and_staff = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
        for user in superusers_and_staff:
            for group in Group.objects.all():
                user_group_default, created = UserGroupDefault.objects.get_or_create(user=user, group=group)
                user_group_default.is_visualizer = True
                user_group_default.save()

post_save.connect(update_existing_superusers_and_staff, sender=Group)