import os
import mimetypes

from django.http.response import HttpResponse

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import Project, TTSData
from .serializers import ProjectSerializer, TTSDataCreateUpdateSerializer, TTSDataSerializer
from .paginations import CustomPageNumberPagination


class ProjectViewSet(ModelViewSet):
    """ 프로젝트 CRUD ViewSet """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'

    def get_queryset(self):
        queryset = Project.objects.filter(user=self.request.user)
        return queryset


class TTSDataViewSet(ModelViewSet):
    """ 프로젝트에 포함된 TTS Data CRUD ViewSet """
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    lookup_field = 'data_id'

    def get_queryset(self):
        """
        프로젝트에 포함된 TTS 데이터 쿼리셋 반환
        """
        project = Project.objects.get(user=self.request.user, project_id=self.kwargs['_project_id'])
        queryset = TTSData.objects.filter(project=project)
        return queryset

    def get_serializer_class(self):
        """
        데이터 생성, 수정 / 조회, 삭제 시리얼라이저 분리
        """
        if hasattr(self, 'action') and self.action in ["create", "update"]:
            return TTSDataCreateUpdateSerializer
        else:
            return TTSDataSerializer

    def perform_destroy(self, instance):
        """
        데이터 삭제시 해당 오디오 파일도 함께 삭제
        """
        if os.path.exists(instance.path):
            os.remove(instance.path)

        instance.delete()

    @action(detail=True, methods=['get'])
    def download(self, request, **kwargs):
        """
        해당 오디오 파일을 송신하는 action

        GET /projects/:id/data/:id/download/
        url로 접근시 해당 파일 다운로드
        """
        instance = self.get_object()
        size = os.path.getsize(instance.path)
        mime_type, _ = mimetypes.guess_type(instance.path)
        with open(instance.path, 'rb') as f:
            res = HttpResponse(f.read(), content_type=mime_type)
            res['Content-Disposition'] = "attachment; filename=%s.mp3" % str(instance.data_id)
            res['Content-Length'] = size
            return res
