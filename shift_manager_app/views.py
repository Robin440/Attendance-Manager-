import base64
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.http import HttpRequest
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import User
from rest_framework.exceptions import ValidationError
from member_manager_app.models import *
from shift_manager_app.models import *
from shift_manager_app.serializers import *
from member_manager_app.serializers import RoleSerializer, OrganizationSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from member_manager_app.models import *
from authenticator_app.models import *
from authenticator_app.serializers import *
from geopy.distance import geodesic
# import face_recognition
import datetime
from django.utils import timezone
from datetime import timedelta
from django.http import Http404
from authenticator_app.permissions import IsRoleAdmin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from shift_manager_app.serializers import *
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# System Location


class SystemLocationCreateView(APIView):

    def get(self, request):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)

            if user_role.name == 'admin':
                queryset = SystemLocation.objects.all()
                serializer = GetSystemLocationSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return Response({"message": "You don't have permission"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid

            data = request.data.copy()  # Make a copy of request data
            data['organization'] = organization_uuid

            serializer = SystemLocationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"message": "system location created", "data": serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SystemLocationRetrieveUpdateDestroyView(APIView):
    serializer_class = GetSystemLocationSerializer
    queryset = SystemLocation.objects.all()

    def get_object(self, uuid):
        return get_object_or_404(self.queryset, uuid=uuid)

    def get(self, request, *args, **kwargs):
        try:
            uuid = kwargs.get('uuid')
            data = SystemLocation.objects.get(uuid=uuid)
            serializer = GetSystemLocationSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    def put(self, request, *args, **kwargs):
        requesting_user = self.request.user
        user_member = get_object_or_404(Member, user=requesting_user)
        organization_uuid = user_member.organization.uuid
        request.data['organization'] = organization_uuid
        try:
            uuid = kwargs.get('uuid')
            sys = self.get_object(uuid)
            serializer = SystemLocationSerializer(sys, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "systemlocation updated", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

    def delete(self, request, *args, **kwargs):
        try:
            uuid = kwargs.get('uuid')
            sys = self.get_object(uuid)
            sys.delete()
            return Response({"message": "system location deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')


class ShiftGetCreateView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsRoleAdmin()]
        return [IsAuthenticated()]

    def get(self, request, format=None):
        try:
            requesting_user = request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            queryset = Shift.objects.filter(
                organization=user_member.organization)

            # Retrieve filters from request
            search = request.GET.get('search')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            status = request.GET.get('status')
            created_by_uuids = request.GET.getlist('created_by_uuids')

            # Apply filters
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | Q(description__icontains=search))

            if start_date and end_date:
                print("entered")
                queryset = queryset.filter(
                    created_at__date__gte=start_date, created_at__date__lte=end_date)

            if status:
                queryset = queryset.filter(status=status)

            if created_by_uuids:
                queryset = queryset.filter(
                    created_by__uuid__in=created_by_uuids)

            page = request.GET.get('page')
            per_page = request.GET.get('per_page')
            if not per_page:
                per_page = 15
            if not page:
                page = 1
            paginator = Paginator(queryset, per_page)  # Show 10 trips per page

            try:
                queryset = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                queryset = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                queryset = paginator.page(paginator.num_pages)

            serializer = GetShiftSerializer(queryset, many=True)
            return Response({
                'data': serializer.data,
                'paginator': {
                    'num_pages': paginator.num_pages,
                    'page': queryset.number,

                }
            })

            serializer = GetShiftSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)})

    def post(self, request, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid
            sys_location = SystemLocation.objects.filter().first()
            # Add organization_id and user_member pk to the data
            data = request.data
            print(organization_uuid)
            data['organization'] = organization_uuid
            data['created_by'] = user_member.pk
            data['updated_by'] = user_member.pk
            data['default_location'] = sys_location.uuid
            # Serialize and save the data
            serializer = ShiftSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Return success response
            return Response({"message": "Shift created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Return error response
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShiftRetrieveUpdateDestroyView(APIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsRoleAdmin]

    def get(self, request, uuid, format=None):
        user = request.user
        organ_id = get_object_or_404(Member, user=user.id)
        shift = Shift.objects.get(
            organization=organ_id.organization, uuid=uuid)

        serializer = self.serializer_class(shift)
        return Response(serializer.data)

    def put(self, request, uuid, format=None):
        user = request.user
        organ_id = get_object_or_404(Member, user=user.id)
        shift = Shift.objects.get(
            organization=organ_id.organization, uuid=uuid)
        request.data['organization'] = organ_id.organization.uuid
        serializer = self.serializer_class(shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "shift updated", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, format=None):
        user = request.user
        organ_id = get_object_or_404(Member, user=user.id)
        shift = Shift.objects.get(
            organization=organ_id.organization, uuid=uuid)
        shift.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShiftScheduleLogGetCreateView(APIView):
    def get(self, request, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)
            if user_role.name == 'admin':
                queryset = ShiftScheduleLog.objects.all()
                serializer = GetShiftScheduleLogSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                queryset = ShiftScheduleLog.objects.filter(member=user_member)
                serializer = ShiftScheduleLogSerializer(queryset, many=True)
                return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid

            data = request.data
            data['organization'] = organization_uuid
            data['member'] = user_member.uuid

            serializer = ShiftScheduleLogSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"shift schedule log": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShiftScheduleLogRetrieveUpdateDestroyView(APIView):
    def get_object(self, uuid):
        return get_object_or_404(ShiftScheduleLog, uuid=uuid)

    def get(self, request, uuid, format=None):
        try:
            shift_schedule_log = self.get_object(uuid)
            serializer = GetShiftScheduleLogSerializer(shift_schedule_log)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, uuid, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid

            data = request.data
            data['organization'] = organization_uuid
            data['member'] = user_member.uuid
            shift_schedule_log = self.get_object(uuid)
            print(shift_schedule_log)

            serializer = ShiftScheduleLogSerializer(
                shift_schedule_log, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "shift schedule log updated", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, format=None):
        try:
            shift_schedule_log = self.get_object(uuid)
            shift_schedule_log.delete()
            return Response({"message": "shift schedule log deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LocationSettingsGetCreateView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)

            uuid = kwargs.get('uuid')

            if user_role.name == 'admin':
                queryset = LocationSettings.objects.all()
            else:
                queryset = LocationSettings.objects.filter(member=user_member)

            serializer = GetLocationSettingsSerializer(queryset, many=True)

            return Response({"data": serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uuid, format=None):
        try:
            shift_schedule_log = get_object_or_404(ShiftScheduleLog, uuid=uuid)
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid

            data = request.data
            data['organization'] = organization_uuid
            serializer = LocationSettingsSerializer(data=request.data)
            if serializer.is_valid():
                start_time = serializer.validated_data['start_time']
                end_time = serializer.validated_data['end_time']
                shift = shift_schedule_log.shift

                if end_time < start_time:
                    end_time += timedelta(days=1)

                if shift.start_time <= start_time <= shift.end_time and shift.start_time <= end_time <= shift.end_time:
                    serializer.save()
                    shift_schedule_log.location_settings.add(
                        serializer.instance)
                    return Response({"message": "Location settings created", "data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    raise ValidationError(
                        {"error": "Location settings times must be within the shift's time range."})
            else:
                raise ValidationError(serializer.errors)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LocationSettingsUpdateDeleteView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)

            uuid = kwargs.get('uuid')

            queryset = LocationSettings.objects.get(uuid=uuid)
            serializer = GetLocationSettingsSerializer(queryset)

            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            uuid = kwargs.get('uuid')

            # Get the requesting user
            requesting_user = self.request.user

            # Get the organization UUID associated with the requesting user
            user_member = get_object_or_404(Member, user=requesting_user)
            organization_uuid = user_member.organization.uuid

            # Retrieve the LocationSettings instance by its UUID
            location_settings = get_object_or_404(LocationSettings, uuid=uuid)

            # Update the data with the organization UUID
            data = request.data
            data['organization'] = organization_uuid

            # Serialize the updated data
            serializer = LocationSettingsSerializer(
                instance=location_settings, data=data)

            # Check if the serializer is valid
            if serializer.is_valid():
                # Save the updated location settings
                serializer.save()
                return Response({"message": "location settings updated", "data": serializer.data})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FRImageView(APIView):

    def get(self, request, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            # user_role = Role.objects.get(uuid=user_member.role)
            print(user_member.role.name)
            if user_member.role.name == 'admin':
                fri = FRImage.objects.all()
                serializer_fri = GetFRImageSerializer(fri, many=True)

                return Response({"data": serializer_fri.data})
            else:
                fri = FRImage.objects.filter(member=user_member)
                serializer_fri = GetFRImageSerializer(fri, many=True)
                return Response({"data": serializer_fri.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            print(user_member)
            fri_data = request.data
            if FRImage.objects.filter(member = user_member).exists():
                return Response("Member FRI image already exists")
            request.data['member'] = user_member.uuid
            request.data['organization'] = user_member.organization.uuid
            print(f'organization === {user_member.organization}')
            #     return Response("Already image saved")
            serializer_fri = FRImageSerializer(
                data=fri_data)  # Pass data to the serializer

            # Check if the serializer is valid
            if serializer_fri.is_valid():
                # Save the serializer data to the database
                # Assuming 'member' is a field in your serializer
                serializer_fri.save(member=user_member)
                return Response({"message": "FRI image created", 'data': serializer_fri.data}, status=status.HTTP_200_OK)
            else:
                # If the serializer is not valid, raise a validation error
                raise ValidationError(serializer_fri.errors)
        except Exception as e:
            # Return the error message in the response
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FRImageDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = FRImageSerializer
    queryset = FRImage.objects.all()
    lookup_field = 'uuid'

    def get_object(self):
        try:
            uuid = self.kwargs.get('uuid')
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.name)

            if user_role.name == 'admin':
                return get_object_or_404(FRImage, uuid=uuid)
            else:
                fr_image = get_object_or_404(
                    FRImage, uuid=uuid, member=user_member)
                if fr_image.member != user_member:
                    raise PermissionDenied(
                        "You don't have permission to access this FR image.")
                return fr_image
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            request.data['member'] = user_member.uuid
            request.data['organization'] = user_member.organization.uuid
            serializer = FRImageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)
            user_role = get_object_or_404(Role, uuid=user_member.role.name)

            if user_role.name == 'admin':
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                if instance.member != user_member:
                    raise PermissionDenied(
                        "You don't have permission to delete this FR image.")
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScanAPIView(ListCreateAPIView):
    serializer_class = MemberScanSerializer

    def get(self, request):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)

            if user_member.role.name == 'admin':
                data = MemberScan.objects.all()

                page = request.GET.get('page')
                per_page = request.GET.get('per_page')
                if not per_page:
                    per_page = 15
                if not page:
                    page = 1
                paginator = Paginator(data, per_page)  # Show 10 trips per page

                try:
                    data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    data = paginator.page(paginator.num_pages)

                serializer = GetMemberScanSerializer(data, many=True)
                return Response({
                    'data': serializer.data,
                    'paginator': {
                        'num_pages': paginator.num_pages,
                        'page': data.number,

                    }
                })

                return Response({"data": serializer.data})
            else:
                data = MemberScan.objects.filter(member=user_member)

                page = request.GET.get('page')
                per_page = request.GET.get('per_page')
                if not per_page:
                    per_page = 15
                if not page:
                    page = 1
                paginator = Paginator(data, per_page)  # Show 10 trips per page

                try:
                    data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    data = paginator.page(paginator.num_pages)

                serializer = GetMemberScanSerializer(data, many=True)
                return Response({
                    'data': serializer.data,
                    'paginator': {
                        'num_pages': paginator.num_pages,
                        'page': data.number,

                    }
                })

                serializer = GetMemberScanSerializer(data)
                return Response({"data": serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            requesting_user = self.request.user
            user_member = get_object_or_404(Member, user=requesting_user)

            shift_schedule_log = ShiftScheduleLog.objects.filter(
                member=user_member).first()
            if not shift_schedule_log:
                return Response({"error": "No shift schedule log found for the member"}, status=status.HTTP_400_BAD_REQUEST)

            shift = shift_schedule_log.shift
            face_image = request.data.get('face_image')

            user_role = get_object_or_404(Role, uuid=user_member.role.uuid)
            # if user_role.name == 'admin':

            #     user_member_uuid = request.data.get('member_uuid')
            #     if not user_member_uuid:
            #         return Response({"error": "Member UUID is required for admin to create a scan"},
            #                         status=status.HTTP_400_BAD_REQUEST)
            #     user_member = get_object_or_404(Member, uuid=user_member_uuid)

            if shift.enable_face_recognition:
                face_image = request.data.get('face_image')
                if not face_image:
                    return Response({"error": "Face image is required"}, status=status.HTTP_400_BAD_REQUEST)

                fr_image = FRImage.objects.get(member=user_member)
                member_face_image = face_recognition.load_image_file(
                    fr_image.image)
                uploaded_face_image = face_recognition.load_image_file(
                    face_image)

                face_distances = face_recognition.face_distance(
                    [member_face_image], uploaded_face_image)
                if face_distances.any() and face_distances[0] > 0.6:
                    return Response({"error": "Face recognition failed"}, status=status.HTTP_400_BAD_REQUEST)

            if shift.enable_geo_fencing:
                user_latitude = request.data.get('latitude')
                user_longitude = request.data.get('longitude')
                if not user_latitude or not user_longitude:
                    return Response({"error": "Latitude and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

                user_location = (float(user_latitude), float(user_longitude))

                if shift_schedule_log.location_settings.exists():
                    valid_location_settings = shift_schedule_log.location_settings.filter(
                        applicable_start_date__lte=datetime.date.today(),
                        applicable_end_date__gte=datetime.date.today()
                    )
                    valid_location_settings_matched = False
                    for location_setting in valid_location_settings:
                        location = (location_setting.latitude,
                                    location_setting.longitude)
                        if geodesic(user_location, location).meters <= location_setting.radius:
                            valid_location_settings_matched = True
                            break
                    # if not valid_location_settings_matched:
                    #     return Response({"error": "User location does not match any valid location settings"},
                    #                     status=status.HTTP_400_BAD_REQUEST)
                else:

                    default_location = shift.default_location
                    if default_location:
                        location = (default_location.latitude,
                                    default_location.longitude)
                        if geodesic(user_location, location).meters > default_location.radius:
                            return Response({"error": "User location does not match default system location"},
                                            status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error": "No location settings or default system location found"},
                                        status=status.HTTP_400_BAD_REQUEST)

            if shift.shift_start_time_restriction:
                current_time = datetime.datetime.now().time()
                if current_time > shift.start_time:
                    return Response({"error": "Cannot check in after shift start time"}, status=status.HTTP_400_BAD_REQUEST)

            if shift.loc_settings_start_time_restriction and shift_schedule_log.location_settings.exists():
                valid_location_settings = shift_schedule_log.location_settings.filter(
                    applicable_start_date__lte=datetime.date.today(),
                    applicable_end_date__gte=datetime.date.today()
                )
                valid_location_settings_start_time_matched = False
                for location_setting in valid_location_settings:
                    if location_setting.start_time <= datetime.datetime.now().time():
                        valid_location_settings_start_time_matched = True
                        break
                if not valid_location_settings_start_time_matched:
                    return Response({"error": "Cannot check in before location settings start time"}, status=status.HTTP_400_BAD_REQUEST)

            face_image_content = face_image.read()

    # Decode the base64-encoded content
            decoded_content = base64.b64decode(face_image_content)

    # Create a ContentFile object
            image_file = ContentFile(decoded_content, name="temp.png")

    # Update request.data with the ContentFile object

            request.data['organization'] = user_member.organization.uuid
            request.data['member'] = user_member.uuid
            request.data['system_location'] = shift.default_location.uuid
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(member=user_member)
                return Response({"message": "member scan done", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def roles_view(request):
    if request.method == 'GET':
        roles = Role.objects.all()

        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=200)
    return Response({'detail': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
