from django.db import models
from django.contrib.auth.models import AbstractUser


# AbstractUser => add/modify any fields
# AbstractBaseUser => wuse this if you want to get the full control over your user model
# BaseUserManeger => Employee.objects = Manager

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = "email" # use the email as username
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.email