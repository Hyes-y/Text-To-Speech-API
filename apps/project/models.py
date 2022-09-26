from django.db import models
from django.conf import settings


class Project(models.Model):
    """ TTS(Text to Speech) 데이터를 포함하는 프로젝트 모델 """
    USER = settings.AUTH_USER_MODEL
    user = models.ForeignKey(USER, on_delete=models.DO_NOTHING, db_column='user_id')
    project_id = models.PositiveIntegerField(verbose_name='프로젝트 ID', unique=True)
    title = models.CharField(verbose_name='프로젝트 이름', max_length=50)
    created_at = models.DateTimeField(verbose_name='생성 시각', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정 시각', auto_now=True)


class TTSData(models.Model):
    """ TTS(Text to Speech) 데이터 모델 """
    SPEED = (
        (0.5, 0.5),
        (1.0, 1.0),
        (1.5, 1.5),
        (2.0, 2.0),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    data_id = models.CharField(verbose_name='데이터 ID', max_length=100, unique=True)
    text = models.CharField(verbose_name='변환 전 텍스트', max_length=300)
    speed = models.FloatField(verbose_name='오디오 속도', choices=SPEED, default=1.0)
    path = models.CharField(verbose_name='파일 경로', max_length=100)
    order = models.PositiveIntegerField(verbose_name='정렬 순서', default=1)
    created_at = models.DateTimeField(verbose_name='생성 시각', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정 시각', auto_now=True)
