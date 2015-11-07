from django import forms
from django.contrib.auth.models import User

class AuthForm(forms.Form):
    username = forms.CharField(max_length=30)
    pwd = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(AuthForm):
    pwd2 = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(widget=forms.EmailInput())
    error = {'password_mismatch': "Passwords don't match",
             'dup_email':"This email is already registered",
             'dup_username':"This username is already taken"}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count():
            self.add_error('email', self.error['dup_email'])
        return email



    def clean_username(self):
        user = self.cleaned_data.get('username')

        if user and User.objects.filter(username = user).count():
            self.add_error('username', self.error['dup_username'])
        return user

    def clean(self):
        data1 = self.cleaned_data.get('pwd')
        data2 = self.cleaned_data.get('pwd2')

        if data1 and data2 and data1 != data2:
            self.add_error('pwd', self.error['password_mismatch'])















