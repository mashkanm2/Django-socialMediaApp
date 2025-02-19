from django.db import models
from enum import Enum
from django.contrib.auth.models import AbstractBaseUser,AbstractUser

from .managers import UserManager

# class UserTypes(Enum):
#     CLIENT='client'
#     PROVIDER='provider'
#     ADMIN='admin'
#     class Meta:
#         ordering = ['ADMIN']

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    user_name=models.CharField(max_length=100,db_index=True,unique=True)
    phone_number=models.CharField(max_length=11,unique=True)
    first_name = models.CharField(max_length=255,blank=True,null=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    date_of_birth = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['email', 'phone_number']
    objects = UserManager()

    def __str__(self):
        return self.user_name
    
    def has_perm(self,perm,obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    def has_module_perms(self,app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin




class OtpCode(models.Model):
    phone_number=models.CharField(max_length=11)
    code=models.PositiveSmallIntegerField()
    created=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number}-{self.code}-{self.created}"
    





