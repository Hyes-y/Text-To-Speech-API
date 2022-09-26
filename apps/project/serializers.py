import os

from .models import Project, TTSData
from apps.account.models import User
from apps.utils import preprocess_data, convert_data

from django.db.models import F
from django.db import transaction
from django.conf import settings

from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    """
    프로젝트 CRUD Serializer
    text: 입력 데이터 (긴 글)
    speed: 속도
    """
    text = serializers.CharField(max_length=300, write_only=True)
    speed = serializers.ChoiceField(choices=TTSData.SPEED, write_only=True)

    class Meta:
        model = Project
        exclude = ('id', )
        read_only_fields = ['project_id', 'user', 'created_at', 'updated_at']
        lookup_field = 'project_id'

    def create(self, validated_data):
        """ 프로젝트 생성 함수 """
        text = validated_data.pop('text', None)
        speed = validated_data.pop('speed', 1.0)

        # 로그인 유저 확인
        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)

        # 프로젝트 id 지정 위해 유저의 프로젝트 개수 계산 (id 지정 방식은 변경 가능)
        cnt = Project.objects.filter(user=user).count()
        obj = self.Meta.model.objects.create(user=user, project_id=cnt+1, **validated_data)

        # 프로젝트의 오디오 파일을 저장할 디렉터리 생성 및 path 지정
        path = os.path.join(settings.MEDIA_ROOT, f"{user.username}{str(obj.project_id)}")
        if not os.path.exists(path):
            os.mkdir(path)

        # 텍스트 전처리 및 오디오 파일 변환
        TTS_data = convert_data([preprocess_data(text), path], speed)

        if not TTS_data:
            raise ValueError("ERROR: 오디오 변환 중 오류가 생겼습니다.")

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
    """
    TTS 데이터 생성, 수정 Serializer
    order: 정렬 순서 필드 (없는 경우 맨 마지막에 추가)
    """
    order = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = TTSData
        fields = ('text', 'speed', 'order')
        read_only_fields = ['data_id', 'created_at', 'updated_at', 'project']

    def validate(self, data):
        """ 데이터 유효성 검증 함수 """
        super().validate(data)

        # 정렬 순서 유효성 검사
        # 유저의 해당 프로젝트의 TTS 데이터 개수를 구해서 입력 받은 'order'가 정렬 순서로 적합한지 확인
        request = self.context.get("request")
        user = User.objects.get(id=request.user.id)
        project_id = self.context.get('view').kwargs['_project_id']
        project = Project.objects.get(user=user, project_id=project_id)
        data_length = TTSData.objects.filter(project=project).count()

        if 'order' in data and (data['order'] > data_length + 1 or data['order'] <= 0):
            raise serializers.ValidationError("ERROR: 순서가 잘못되었습니다.")

        return data

    @transaction.atomic()
    def create(self, validated_data):
        """
        TTS 데이터 생성 함수

        프로젝트 생성때와 다르게 한 문장씩만 생성이 가능하며
        순서를 지정할 수 있음.
        """
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

        if not new_data:
            raise ValueError("ERROR: 오디오 변환 중 오류가 생겼습니다.")

        if not order:
            # 정렬 순서가 null 인 경우 맨 마지막(len(data) + 1) 에 추가
            order = len(data) + 1
        else:
            # null이 아닌 경우 해당 순서와 같거나 큰 order 값을 지닌 오브젝트의 값 변경
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
        """ TTS 데이터 수정 함수 """
        text = validated_data.get('text', None)
        speed = validated_data.get('speed', 1.0)

        # 텍스트를 변경한 경우 오디오 파일을 생성하고 관련 필드(data_id, text, path) 모두 변경
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
            if not TTS_data:
                raise ValueError("ERROR: 오디오 변환 중 오류가 생겼습니다.")

            instance.data_id = TTS_data[0][0]
            instance.text = TTS_data[0][1]
            instance.path = os.path.join(path, f'{TTS_data[0][0]}.mp3')

        instance.speed = speed
        instance.save()

        return instance


class TTSDataSerializer(serializers.ModelSerializer):
    """ TTS 데이터 조회 및 삭제 Serializer """
    class Meta:
        model = TTSData
        exclude = ('id', 'path')
        read_only_fields = ('order', 'data_id', 'text', 'speed', 'created_at', 'updated_at')
