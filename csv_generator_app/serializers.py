from rest_framework import serializers
from .models import *

class ExportRequestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportRequestModel
        fields = '__all__'
