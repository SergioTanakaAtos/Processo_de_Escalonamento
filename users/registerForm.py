from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuário',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirmar senha',
        }
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and not email.endswith('@atos.net'):
            raise forms.ValidationError("O e-mail fornecido não é válido.")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso.")
        return email
    def clean_permissions(self):
        permissions = self.cleaned_data.get('permissions')
        if not permissions:
            return []
        group_names = permissions.split(',')
        groups = Group.objects.filter(name__in=group_names)
        if len(groups) != len(group_names):
            raise forms.ValidationError("Um ou mais grupos fornecidos não são válidos.")
        return [group.id for group in groups]