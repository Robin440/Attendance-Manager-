from django.contrib import admin
from shift_manager_app.models import *
# Register your models here.

admin.site.register(Member)
admin.site.register(SystemLocation)
admin.site.register(Shift)
admin.site.register(ShiftScheduleLog)
admin.site.register(FRImage)
admin.site.register(LocationSettings)
admin.site.register(MemberScan)
admin.site.register(Attendance)