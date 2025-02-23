from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import BaseUser,OtpCode
from .forms import UserChangeForm, UserRegisterFormAdmin

@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display=('phone_number','code','created')

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserRegisterFormAdmin

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
admin.site.register(BaseUser,UserAdmin) 