import csv
import django
django.setup()
import os
from django.conf import settings
from celery import shared_task
from .models import ExportRequestModel
from shift_manager_app.models import Attendance, MemberScan, Member


import csv
from django.conf import settings
import os
from shift_manager_app.models import Attendance

@shared_task
def export_data_task(export_request_id):
    export_request = ExportRequestModel.objects.get(uuid=export_request_id)
    if export_request.status == 'pending':
        attendance_data = Attendance.objects.all()
        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'export_{export_request.uuid}.csv')

        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write header row using model field names
            header_row = ['UUID', 'Organization', 'Member', 'Shift', 'Attendance Date']
            csv_writer.writerow(header_row)

            # Write data rows
            for attendance in attendance_data:
                # Assuming organization, member, shift are ForeignKey fields
                organization_name = attendance.organization.name if attendance.organization else ''
                member_name = attendance.member.user.username if attendance.member else ''
                shift_name = attendance.shift.name if attendance.shift else ''
                
                data_row = [attendance.uuid, organization_name, member_name, shift_name, attendance.attendance_date]
                csv_writer.writerow(data_row)

        export_request.path = csv_file_path
        export_request.status = 'completed'
        export_request.save()
