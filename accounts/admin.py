from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import UserChangeForm, UserRegisterForm
from .models import User

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserRegisterForm

    list_display=('user_name','email','phone_number','is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('user_name', 'email', 'phone_number','password')}),
        ("Personal info", {"fields": ('first_name','last_name',"date_of_birth")}),
        ('Permissions', {'fields': ('is_active','is_admin','last_login')}),
    )
    add_fieldsets = (
        (None,{'fields':('user_name','email','phone_number','password1','password2')}),
    )

    search_fields=('user_name','email')
    ordering = ('user_name',)
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(User,UserAdmin) 