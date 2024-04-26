from django.db import models
import uuid




class Role(models.Model):
    uuid  = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100)

class Organization(models.Model):
    uuid  = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
