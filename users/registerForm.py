from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permissão"
    )

    class Meta:
        model = User
        fields = ['first_name', 'email', 'password1', 'password2', 'permissions']
        labels = {
            'first_name': 'Nome',
            'email': 'E-mail',
            'password1': 'Senha',
            'password2': 'Confirmar senha',
            'permissions': 'Permissão'
        }
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('password1')
        confirmar_senha = cleaned_data.get('password2')
        email = cleaned_data.get('email')

        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")

        if email and not email.endswith('@atos.net'):
            raise forms.ValidationError("O e-mail fornecido não é válido.")