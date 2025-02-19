
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, user_name,email,phone_number, password):
        if not user_name:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email address')
        if not phone_number:
            raise ValueError('Users must have a phone number')
        user = self.model(user_name=user_name,email=self.normalize_email(email=email),phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,user_name,email,phone_number,password):
        user=self.create_user(user_name,email,phone_number,password)
        user.is_admin=True
        user.save(using=self._db)
        return user
    
