
from django import forms
from .models import User
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

class UserRegisterForm(forms.ModelForm):
    password1=forms.CharField(label="password",widget=forms.PasswordInput)
    password2=forms.CharField(label="confirm password",widget=forms.PasswordInput)

    class Meta:
        model=User
        fields=('user_name','email','phone_number','first_name','last_name')
        ## TODO : check input to create in manager
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    
    def save(self,commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
    
        return user

class UserChangeForm(forms.ModelForm):
    password=ReadOnlyPasswordHashField(help_text="you can change password in change <a href=\"../password/\">password page</a>")

    class Meta:
        model=User
        fields=('user_name','email','phone_number','password','first_name','last_name')
