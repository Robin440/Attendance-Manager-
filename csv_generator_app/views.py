import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from .export_logic import *
from .serializers import *
from rest_framework.decorators import api_view
from csv_generator_app.tasks import export_data_task
from django.http import JsonResponse
from django.urls import reverse
from .models import ExportRequestModel
from shift_manager_app.models import Attendance
from django.core.serializers.json import DjangoJSONEncoder


@csrf_exempt
@csrf_exempt
def export_request(request):
    if request.method == 'POST':
        try:
            attendance_uuids = [str(attendance.uuid) for attendance in Attendance.objects.all()]
            user = request.user
            print(user)
            user_member = get_object_or_404(Member, user=user)

            export_request = ExportRequestModel.objects.create(
                content={
                    'attendance': attendance_uuids,
                },
                status='pending',
                member=user_member
            )
            export_request_uuid = export_request.uuid
            export_request_uuid = str(export_request_uuid)
            export_data_task.apply_async(args=[export_request_uuid])
  # Convert export_request_uuid to string

            return JsonResponse({'export_request_uuid': str(export_request.uuid)})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def export_request_status(request, export_request_id):
    try:
        export_request = ExportRequestModel.objects.get(pk=export_request_id)
        
        if export_request.status == 'completed':
        
            if not os.path.exists(export_request.path):
                return HttpResponseNotFound('CSV file not found')

            
            download_url = settings.MEDIA_URL + f'export_{export_request.uuid}.csv'
            return JsonResponse({'status': export_request.status, 'download_url': download_url})
        else:
            return JsonResponse({'status': export_request.status})
        
    except ExportRequestModel.DoesNotExist:
        return JsonResponse({'error': 'Export request not found'}, status=404)