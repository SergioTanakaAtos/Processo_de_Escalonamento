from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "As senhas não coincidem.",
    }

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar senha'

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.error_messages = {
                'required': f'Por favor, preencha o campo {field.label}.',
                'invalid': f'{field.label} inválido.',
            }

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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email')
        username = email.split('@')[0]
        user.username = username

        if commit:
            user.save()
        return user
