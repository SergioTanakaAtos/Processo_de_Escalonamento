# Generated by Django 5.0.3 on 2024-05-16 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalation', '0004_logpermission_delete_log_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='escalation',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
    ]
