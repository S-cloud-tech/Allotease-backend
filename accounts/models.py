from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import message
from django_resized import ResizedImageField
import uuid


# This is the folder where profile images are stored
def upload_location(instance, filename):
    file_path = "profile_image/{user_id}/{image}".format(
        user_id=str(instance.id), image=filename
    )
    return file_path


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if email is None:
            raise TypeError('User should have an Email')
        
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None):
        if password is None:
            raise TypeError('Password should not be empty')
        if username is None:
            raise TypeError('User should have a Username')
        
        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, db_index=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name="date joined",   auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

    # Custom fields
    profile_image = ResizedImageField(size=[100, 100], upload_to=upload_location, default="avatar.png",blank=True, 
                                      null=True,)  # Where user is registering
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    


    USERNAME_FIELD = 'email'

    objects = AccountManager()

    def __str__(self):
        return self.email
