from django.contrib import admin

# Register your models here.
from member_manager_app.models import *

admin.site.register(Role)
admin.site.register(Organization)
