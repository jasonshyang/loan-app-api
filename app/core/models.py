from django.db import models

from decimal import Decimal

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

# Constants
ACCOUNT_TYPES = [
    ('BORROWER', 'Borrower'),
    ('LENDER', 'Lender'),
]


# Create your models here.
class UserManager(BaseUserManager):
    '''Manager for the user model'''
    def create_user(self, email, password=None, **kwargs):
        '''Create a new user and return it'''
        if not email:
            raise ValueError('User missing an email address')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password) # encrypt the password
        user.save(using=self._db) # support multiple databases

        return user

    def create_superuser(self, email, password):
        '''Create a new superuser and return it'''
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    '''Custom user model'''
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Account(models.Model):
    '''Model for a user account'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=ACCOUNT_TYPES, default='BORROWER')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.00))

    def __str__(self):
        return self.user.email

class MoneyRequest(models.Model):
    '''Model for a money request'''
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrower',
    )
    lender = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='lender',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=255)
    term = models.IntegerField()

    def __str__(self):
        return self.title