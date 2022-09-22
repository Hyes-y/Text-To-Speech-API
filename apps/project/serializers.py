from rest_framework import serializers
from .models import Project, TTSData


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ('id', )
        read_only_fields = ['project_id', 'user', 'created_at', 'updated_at']


class TTSDataSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(write_only=True)

    class Meta:
        model = TTSData
        exclude = ('id', )
        read_only_fields = ['data_id', 'path', 'created_at', 'updated_at']

