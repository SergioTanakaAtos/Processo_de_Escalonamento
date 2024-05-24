from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'Nome',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirmar senha',
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and not email.endswith('@atos.net'):
            raise forms.ValidationError("O e-mail fornecido não é válido.")


        if email and not email.endswith('@atos.net'):
            raise forms.ValidationError("O e-mail fornecido não é válido.")
        
    def clean_permissions(self):
        permissions = self.cleaned_data.get('permissions')
        if not permissions:
            return []
        group_names = permissions.split(',')
        groups = Group.objects.filter(name__in=group_names)
        if len(groups) != len(group_names):
            raise forms.ValidationError("Um ou mais grupos fornecidos não são válidos.")
        return [group.id for group in groups]