from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django_resized import ResizedImageField
from wallet.models import Virtual_accounts


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
    
    def create_superuser(self, email, password=None):
        if password is None:
            raise TypeError('Password should not be empty')
        if email is None:
            raise TypeError('User should have an email')
        
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class Account(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('regular', 'Regular User'),
        ('merchant', 'Merchant'),
    )

    email = models.EmailField(verbose_name="email", max_length=60, unique=True, db_index=True)
    username = models.CharField(max_length=30, null=True, blank=True, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    business_name = models.CharField(max_length=255, blank=True, null=True)  # Only for merchants
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
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    paystack_virtual_account = models.JSONField(null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    


    USERNAME_FIELD = 'email'

    objects = AccountManager()

    def __str__(self):
        return self.email



class Merchant(models.Model):

    INDIVIDUAL = 'INDIVIDUAL'
    COMPANY = 'COMPANY'
    NONPROFIT = 'NONPROFIT'
    EDUCATIONAL = 'EDUCATIONAL'
    GOVERNMENT = 'GOVERNMENT'

    MERCHANT_TYPE = [
        ('INDIVIDUAL','INDIVIDUAL'),
        ('COMPANY','COMPANY'),
        ('NONPROFIT','NONPROFIT'),
        ('EDUCATIONAL','EDUCATIONAL'),
        ('GOVERNMENT','GOVERNMENT'),
    ]


    user = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    wallet = models.OneToOneField(Virtual_accounts, on_delete=models.CASCADE, null=True, unique=True)
    active          = models.BooleanField(default=True)
    is_verified     = models.BooleanField(default=False)
    is_online       = models.BooleanField(default=False)
    completed_tickets = models.IntegerField(default = 0, null=True, blank = True)
    cancelled_tickets = models.IntegerField(default = 0, null=True, blank = True)
    total_created_tickets     = models.IntegerField(default = 0, null=True, blank = True)
