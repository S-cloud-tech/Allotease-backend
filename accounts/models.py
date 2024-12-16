# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# from django.core.mail import message
# from django_resized import ResizedImageField
# import uuid


# # This is the folder where profile images are stored
# def upload_location(instance, filename):
#     file_path = "profile_image/{user_id}/{image}".format(
#         user_id=str(instance.id), image=filename
#     )
#     return file_path


# class AccountManager(BaseUserManager):
#     def create_user(self, email, password=None):
#         if not email:
#             raise ValueError("User must have an email address")
        
#         user = self.model(
#             email=email,
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         return user
    
#     def create_superuser(self, email, password):
#         user = self.create_user(
#             email=email,
#             password=password,
#         )

#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


# class Account(AbstractBaseUser):
#     email = models.EmailField(verbose_name="email", max_length=60)
#     username = models.CharField(max_length=30, null=True, blank=True)
#     date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
#     last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
#     is_admin = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     is_verified = models.BooleanField(default=False)
#     first_name = models.CharField(max_length=30, null=True, blank=True)
#     last_name = models.CharField(max_length=30, null=True, blank=True)
#     fullname = models.CharField(max_length=50, null=True, blank=True)

#     # Custom fields
#     profile_image = ResizedImageField(size=[100, 100], upload_to=upload_location, default="avatar.png",
#                                       blank=True, null=True,
#                                       )  # Where user is registering
    


#     USERNAME_FIELD = "email"
