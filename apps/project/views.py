from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Project, TTSData
from .serializers import ProjectSerializer, TTSDataCreateUpdateSerializer, TTSDataSerializer
import os
from django.http.response import HttpResponse
import mimetypes

class ProjectViewSet(ModelViewSet):
    """ 프로젝트 CRUD ViewSet """
    # permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'

    def get_queryset(self):
        # queryset = Project.objects.filter(user=self.request.user)
        # test
        queryset = Project.objects.all()
        return queryset


class TTSDataViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    # pagination_class =
    lookup_field = 'data_id'

    def get_queryset(self):
        queryset = TTSData.objects.filter(project=self.kwargs['project_project_id'])
        return queryset

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action in ["create", "update"]:
            return TTSDataCreateUpdateSerializer
        else:
            return TTSDataSerializer

    def perform_destroy(self, instance):
        if os.path.exists(instance.path):
            os.remove(instance.path)

        instance.delete()

    @action(detail=True, methods=['get'])
    def download(self, request, project_project_id, data_id):
        instance = self.get_object()
        size = os.path.getsize(instance.path)
        mime_type, _ = mimetypes.guess_type(instance.path)
        with open(instance.path, 'rb') as f:
            res = HttpResponse(f.read(), content_type=mime_type)
            res['Content-Disposition'] = "attachment; filename=%s.mp3" % str(instance.data_id)
            res['Content-Length'] = size
            return res
