from django import forms
from django.contrib.auth import get_user_model
        
User = get_user_model()
class LoginForm(forms.Form):
    username = forms.CharField(
                    widget=forms.TextInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':'Username'   
                        }
                    )
                )
    password = forms.CharField(min_length=4,
                    widget=forms.PasswordInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':''   
                        }
                    )
                )

class SignupForm(forms.Form):
    username = forms.CharField(label='Username',
                    widget=forms.TextInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':'Your username'   
                        }
                    )
                )
    email = forms.CharField(label='Email',
                    widget=forms.EmailInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':'Your email'   
                        }
                    )
                )
    password = forms.CharField(label='Password', min_length=4,
                    widget=forms.PasswordInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':''   
                        }
                    )
                )
    cpassword = forms.CharField(label='Confirm Password', min_length=4,
                    widget=forms.PasswordInput(
                        attrs={
                            'class':'form-control col-12',
                            'placeholder':''   
                        }
                    )
                )
    def clean(self):
        passwd = self.cleaned_data.get('password')
        cpasswd = self.cleaned_data.get('cpassword')
        if passwd != cpasswd:
            raise forms.ValidationError("Password and Confirm Password must match.")
        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if(qs.exists()):
            raise forms.ValidationError("Username is already registered try someother username")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if(qs.exists()):
            raise forms.ValidationError("Email address is already registered")
        return email