import os

from .models import Project, TTSData
from apps.account.models import User
from apps.utils import preprocess_data, convert_data

from django.db.models import F
from django.db import transaction
from django.conf import settings

from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=300, write_only=True)
    speed = serializers.ChoiceField(choices=TTSData.SPEED, write_only=True)

    class Meta:
        model = Project
        exclude = ('id', )
        read_only_fields = ['project_id', 'user', 'created_at', 'updated_at']
        lookup_field = 'project_id'

    def create(self, validated_data):
        text = validated_data.pop('text', None)
        speed = validated_data.pop('speed', 1.0)

        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)

        cnt = Project.objects.filter(user=user).count()

        obj = self.Meta.model.objects.create(user=user, project_id=cnt+1, **validated_data)
        path = os.path.join(settings.MEDIA_ROOT, f"{user.username}{str(obj.project_id)}")
        if not os.path.exists(path):
            os.mkdir(path)
        TTS_data = convert_data([preprocess_data(text), path], speed)
        tts_obj = [
            TTSData(
                data_id=val[0],
                text=val[1],
                speed=speed,
                order=idx+1,
                path=os.path.join(path, f'{val[0]}.mp3'),
                project=obj
            )
            for idx, val in enumerate(TTS_data)]

        TTSData.objects.bulk_create(tts_obj)
        return obj


class TTSDataCreateUpdateSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = TTSData
        fields = ('text', 'speed', 'order')
        read_only_fields = ['data_id', 'created_at', 'updated_at', 'project']

    def validate(self, data):
        super().validate(data)
        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)
        project_id = self.context.get('view').kwargs['_project_id']
        project = Project.objects.get(user=user, project_id=project_id)
        data_length = TTSData.objects.filter(project=project).count()
        print(data_length)
        if 'order' in data and (data['order'] > data_length + 1 or data['order'] <= 0):
            raise serializers.ValidationError("ERROR: 순서가 잘못되었습니다.")

        return data

    @transaction.atomic()
    def create(self, validated_data):
        text = validated_data.get('text', None)
        speed = validated_data.get('speed', 1.0)
        order = validated_data.get('order', None)
        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)
        project_id = self.context.get('view').kwargs['_project_id']
        project = Project.objects.get(user=user, project_id=project_id)
        data = TTSData.objects.filter(project=project)

        path = os.path.join(settings.MEDIA_ROOT, f"{user.username}{str(project_id)}")
        if not os.path.exists(path):
            os.mkdir(path)
        new_data = convert_data([preprocess_data(text), path], speed)
        if len(new_data) != 1:
            raise ValueError("ERROR: 한 문장씩 추가 가능합니다.")

        if not order:
            order = len(data) + 1
        else:
            for data_obj in data.iterator():
                if data_obj.order >= order:
                    data_obj.order = F('order') + 1
                    data_obj.save()

        return TTSData.objects.create(
                data_id=new_data[0][0],
                text=new_data[0][1],
                speed=speed,
                path=os.path.join(path, f'{new_data[0][0]}.mp3'),
                order=order,
                project=project
        )

    def update(self, instance, validated_data):
        text = validated_data.get('text', None)
        speed = validated_data.get('speed', 1.0)

        if preprocess_data(text)[0] != instance.text:
            if os.path.exists(instance.path):
                os.remove(instance.path)

            path = os.path.join(
                settings.MEDIA_ROOT,
                f"{instance.project.user.username}{str(instance.project.project_id)}"
            )
            TTS_data = convert_data([preprocess_data(text), path], speed)
            if len(TTS_data) != 1:
                raise ValueError("ERROR: 한 문장씩 수정 가능합니다.")

            instance.data_id = TTS_data[0][0]
            instance.text = TTS_data[0][1]
            instance.path = os.path.join(path, f'{TTS_data[0][0]}.mp3')

        instance.speed = speed
        instance.save()

        return instance


class TTSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TTSData
        exclude = ('id', 'path')
        read_only_fields = ('order', 'data_id', 'text', 'speed', 'created_at', 'updated_at')
