from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "As senhas não coincidem.",
    }

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar senha'

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.error_messages = {
                'required': f'Por favor, preencha o campo {field.label}.',
                'invalid': f'{field.label} inválido.',
            }

        self.fields['username'].error_messages['unique'] = 'Este nome de usuário já está em uso.'
        self.fields['email'].error_messages['unique'] = 'Este e-mail já está em uso.'
        
        self.fields['password1'].error_messages.update({
            'required': 'Por favor, preencha o campo Senha.',
        })
        self.fields['password2'].error_messages.update({
            'required': 'Por favor, preencha o campo Confirmar senha.',
        })

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        if len(password2) > 0 and len(password2) < 8:
            raise forms.ValidationError("A senha deve conter no mínimo 8 caracteres.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and not email.endswith('@atos.net'):
            self.add_error('email', "O e-mail fornecido não é válido.")

        return cleaned_data

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
