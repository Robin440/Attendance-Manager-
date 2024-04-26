from django.db import models
import uuid

from authenticator_app.models import *
from member_manager_app.models import *
from member_manager_app.serializers import OrganizationSerializer, RoleSerializer
from authenticator_app.serializers import UserSerializer

class Shift(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=200, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    default_location = models.ForeignKey('SystemLocation', on_delete=models.SET_NULL, blank=True, null=True)
    enable_face_recognition = models.BooleanField(default=True)
    enable_geo_fencing = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    shift_start_time_restriction = models.BooleanField(default=True)
    loc_settings_start_time_restriction = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('Member', on_delete=models.SET_NULL, related_name='created_shifts', blank=True, null=True)
    updated_by = models.ForeignKey('Member', on_delete=models.SET_NULL, related_name='updated_shifts', blank=True, null=True)
    present_working_hours = models.FloatField(default=8.0)
   
    
class SystemLocation(models.Model):
        uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
        organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
        name = models.CharField(max_length=200)
        description = models.CharField(max_length=200, blank=True)
        latitude = models.DecimalField(max_digits=9, decimal_places=7)
        longitude = models.DecimalField(max_digits=9, decimal_places=7)
        radius = models.FloatField(default=50.0)
        status = models.CharField(max_length=10, default="active")
        updated_at = models.DateTimeField(auto_now=True)

class LocationSettings(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    system_location = models.ForeignKey(SystemLocation, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    applicable_start_date = models.DateField()
    applicable_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('Member', on_delete=models.SET_NULL, related_name='created_locationsettings', blank=True, null=True)
    updated_by = models.ForeignKey('Member', on_delete=models.SET_NULL, related_name='updated_locationsettings', blank=True, null=True)




class Member(models.Model):
    
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_manager_members')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class FRImage(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='fr_images/')
    updated_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

class MemberScan(models.Model):
    SCAN_TYPE_CHOICES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ]
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    system_location = models.ForeignKey(SystemLocation, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='member_scans/')
    date_time = models.DateTimeField()
    latitude = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES) 
    created_at = models.DateTimeField(auto_now_add=True)

class ShiftScheduleLog(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    location_settings = models.ManyToManyField(LocationSettings, blank=True)

class Attendance(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    scans = models.ManyToManyField(MemberScan)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
