from rest_framework import serializers
from .models import *
from member_manager_app.models import *
from member_manager_app.serializers import RoleSerializer, OrganizationSerializer
from authenticator_app.serializers import UserSerializer


class ShiftSerializer(serializers.ModelSerializer):
    # organization= OrganizationSerializer(read_only=True)
    class Meta:
        model = Shift
        fields = '__all__'


class SystemLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemLocation
        fields = '__all__'


class GetSystemLocationSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = SystemLocation
        fields = '__all__'


class LocationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationSettings
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = '__all__'


class FRImageSerializer(serializers.ModelSerializer):
    # organization = OrganizationSerializer(read_only = True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = FRImage
        fields = '__all__'


class MemberScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberScan
        fields = '__all__'


class ShiftScheduleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftScheduleLog
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class GetShiftScheduleLogSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = ShiftScheduleLog
        fields = '__all__'


class GetMemberScanSerializer(serializers.ModelSerializer):
    system_location = SystemLocationSerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = MemberScan
        fields = '__all__'


class GetFRImageSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    # role = RoleSerializer(read_only=True)
    member = MemberSerializer()

    class Meta:
        model = FRImage
        fields = '__all__'


class GetLocationSettingsSerializer(serializers.ModelSerializer):

    organization = OrganizationSerializer()
    system_location = SystemLocationSerializer()

    class Meta:
        model = LocationSettings
        fields = '__all__'


class GetShiftSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    default_location = SystemLocationSerializer()
    created_by = MemberSerializer()
    updated_by = MemberSerializer()

    class Meta:
        model = Shift
        fields = '__all__'


class GetLocationSettingsSerializer(serializers.ModelSerializer):
    system_location = SystemLocationSerializer()
    organization = OrganizationSerializer()
    created_by = MemberSerializer()
    updated_by = MemberSerializer()

    class Meta:
        model = LocationSettings
        fields = '__all__'
