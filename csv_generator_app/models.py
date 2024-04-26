from django.db import models
import uuid
from shift_manager_app.models import Member

class ExportRequestModel(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    content = models.JSONField()
    path = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
   
  