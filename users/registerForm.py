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
        email = cleaned_data.get('email')


        if email and not email.endswith('@atos.net'):
            raise forms.ValidationError("O e-mail fornecido não é válido.")