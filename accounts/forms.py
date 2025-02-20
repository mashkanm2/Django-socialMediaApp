
from django import forms
from .models import User
from django.db.models import Q
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

class UserRegisterFormAdmin(forms.ModelForm):
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
    
    def clean(self):
        cleaned_data = super().clean()
        user_nm=cleaned_data.get('user_name')
        email_=cleaned_data.get('email')
        phone_number_=cleaned_data.get('phone_number')
        if user_nm and email_ and phone_number_:
            # Check if user_name,email and phone_number exists
            ret_exist=User.objects.filter(Q(user_name=user_nm) |
                                Q(email=email_) |
                                Q(phone_number=phone_number_)).exists()
            if ret_exist:
                raise ValidationError('user_name | email | phone_number  already exists')
        
        return cleaned_data

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


class UserRegistrationForm(forms.Form):
    user_name=forms.CharField(max_length=100,required=True)
    email=forms.EmailField(max_length=255,required=True)
    phone_number=forms.CharField(max_length=11,required=True)
    # first_name=forms.CharField(max_length=255,required=False)
    # last_name=forms.CharField(max_length=255,required=False)
    # date_of_birth=forms.DateField(required=False)
    password=forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()

        # Check if user_name exists
        # if User.objects.filter(user_name=cleaned_data['user_name']).exists():
        #     messages.error(request, 'Username already exists', 'error')
            
        # # Check if email exists
        # if User.objects.filter(email=cleaned_data['email']).exists():
        #     messages.error(request, 'Email already exists', 'error')
            
        # # Check if phone_number exists
        # if User.objects.filter(phone_number=cleaned_data['phone_number']).exists():
        #     messages.error(request, 'Phone number already exists', 'error')

        ## search by one query
        user_nm=cleaned_data.get('user_name')
        email_=cleaned_data.get('email')
        phone_number_=cleaned_data.get('phone_number')
        if user_nm and email_ and phone_number_:
            # Check if user_name,email and phone_number exists
            ret_exist=User.objects.filter(Q(user_name=user_nm) |
                                Q(email=email_) |
                                Q(phone_number=phone_number_)).exists()
            if ret_exist:
                raise ValidationError('user_name | email | phone_number  already exists')
        
        return cleaned_data


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()
