from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.
class User(AbstractUser):
    uuid  = models.UUIDField(default=uuid.uuid4, editable=True)
    
    class Meta:
       
        app_label = 'authenticator_app'