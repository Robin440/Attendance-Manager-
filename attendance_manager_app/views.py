from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework import status
from django.utils import timezone
from shift_manager_app.models import *
from shift_manager_app.serializers import *
from member_manager_app.models import Role
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework.response import Response

class GetAttendanceAPIView(ListCreateAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)
        
            if user_role.name == 'admin':
                return Attendance.objects.all()
            else:
                return Attendance.objects.filter(member=user_member)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class ComputeAttendanceApi(ListCreateAPIView):
    serializer_class = AttendanceSerializer
 
    def perform_create(self, serializer):
    
        requesting_user = self.request.user
        print(requesting_user)
        user_member = get_object_or_404(Member, user=requesting_user)
        print(user_member)
        
        user_role = get_object_or_404(Role, uuid=user_member.role.uuid)
        
       
       
        if user_role.name == 'admin':
          
            assigned_logs = ShiftScheduleLog.objects.filter(status='active')

            for log in assigned_logs:
                shift = log.shift
                member = log.member
                today = timezone.now().date()
                scans_today = MemberScan.objects.filter(member=member, date_time__date=today)
                print(scans_today)
                total_working_hours = 0.0
                previous_scan = None
                for scan in scans_today:
                    if scan.scan_type == 'check_in':
                        if previous_scan and previous_scan.scan_type == 'check_out':
                            time_difference = scan.date_time - previous_scan.date_time
                            total_working_hours += time_difference.total_seconds() / 3600
                        previous_scan = scan
                    elif scan.scan_type == 'check_out':
                        previous_scan = None

                if total_working_hours >= shift.present_working_hours:
                    attendance_date = timezone.now().date()

                   
                    serialized_scans = MemberScanSerializer(scans_today, many=True).data

                 
                    data = {
                        'member': member.pk,
                        'shift': shift.pk,
                        'attendance_date': attendance_date,
                        'scans': serialized_scans
                    }

                    serializer.save(**data)
        else:
            raise PermissionDenied("Only admin users can create attendance records.")

    def perform_destroy(self, instance):
        raise MethodNotAllowed("DELETE method is not allowed.")
