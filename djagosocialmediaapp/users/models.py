from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager as BUM
from django.contrib.auth.models import PermissionsMixin



class BaseUserManager(BUM):
    def create_user(self, user_name,email,phone_number, password,activate=True):
        if not user_name:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email address')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        user = self.model(user_name=user_name,email=self.normalize_email(email=email),phone_number=phone_number)
        user.set_password(password)
        user.is_active=activate
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self,user_name,email,phone_number,password):
        user=self.create_user(user_name,email,phone_number,password)
        user.is_admin=True
        user.save(using=self._db)
        return user


class BaseUser(AbstractBaseUser, PermissionsMixin):

    user_name=models.CharField(max_length=100,unique=True,db_index=True)
    email = models.EmailField(verbose_name = "email address")
    phone_number=models.CharField(max_length=11)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = BaseUserManager()

    USERNAME_FIELD = 'user_name'
    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return self.email

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
        return self.is_admin


class OtpCode(models.Model):
    phone_number=models.CharField(max_length=11)
    code=models.PositiveSmallIntegerField()
    created=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number}-{self.code}-{self.created}"
    


class UserProfile(models.Model):
    user=models.OneToOneField(BaseUser,on_delete=models.CASCADE,primary_key=True)
    first_name = models.CharField(max_length=255,default='')
    last_name = models.CharField(max_length=255,default='')
    date_of_birth = models.DateField(null=True,blank=True)
    profile_picture = models.TextField(null=True,blank=True)
    city_address=models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name}-{self.last_name}"





