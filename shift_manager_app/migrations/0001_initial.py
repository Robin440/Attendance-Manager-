# Generated by Django 4.2.11 on 2024-04-26 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('member_manager_app', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationSettings',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('applicable_start_date', models.DateField()),
                ('applicable_end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_manager_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('enable_face_recognition', models.BooleanField(default=True)),
                ('enable_geo_fencing', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('shift_start_time_restriction', models.BooleanField(default=True)),
                ('loc_settings_start_time_restriction', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('present_working_hours', models.FloatField(default=8.0)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_shifts', to='shift_manager_app.member')),
            ],
        ),
        migrations.CreateModel(
            name='SystemLocation',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('latitude', models.DecimalField(decimal_places=7, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=7, max_digits=9)),
                ('radius', models.FloatField(default=50.0)),
                ('status', models.CharField(default='active', max_length=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
            ],
        ),
        migrations.CreateModel(
            name='ShiftScheduleLog',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('status', models.CharField(default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location_settings', models.ManyToManyField(blank=True, to='shift_manager_app.locationsettings')),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.member')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.shift')),
            ],
        ),
        migrations.AddField(
            model_name='shift',
            name='default_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shift_manager_app.systemlocation'),
        ),
        migrations.AddField(
            model_name='shift',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization'),
        ),
        migrations.AddField(
            model_name='shift',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_shifts', to='shift_manager_app.member'),
        ),
        migrations.CreateModel(
            name='MemberScan',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='member_scans/')),
                ('date_time', models.DateTimeField()),
                ('latitude', models.CharField(max_length=200)),
                ('longitude', models.CharField(max_length=200)),
                ('scan_type', models.CharField(choices=[('check_in', 'Check In'), ('check_out', 'Check Out')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.member')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
                ('system_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.systemlocation')),
            ],
        ),
        migrations.AddField(
            model_name='locationsettings',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_locationsettings', to='shift_manager_app.member'),
        ),
        migrations.AddField(
            model_name='locationsettings',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization'),
        ),
        migrations.AddField(
            model_name='locationsettings',
            name='system_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.systemlocation'),
        ),
        migrations.AddField(
            model_name='locationsettings',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_locationsettings', to='shift_manager_app.member'),
        ),
        migrations.CreateModel(
            name='FRImage',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('image', models.ImageField(upload_to='fr_images/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.member')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('attendance_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.member')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='member_manager_app.organization')),
                ('scans', models.ManyToManyField(to='shift_manager_app.memberscan')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shift_manager_app.shift')),
            ],
        ),
    ]
