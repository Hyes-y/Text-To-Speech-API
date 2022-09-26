import os
import mimetypes
from .models import Project, TTSData
from .serializers import ProjectSerializer, TTSDataCreateUpdateSerializer, TTSDataSerializer
from .paginations import CustomPageNumberPagination

from django.http.response import HttpResponse

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


class ProjectViewSet(ModelViewSet):
    """ 프로젝트 CRUD ViewSet """
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'

    def get_queryset(self):
        queryset = Project.objects.filter(user=self.request.user)
        return queryset


class TTSDataViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    lookup_field = 'data_id'

    def get_queryset(self):
        print(self.kwargs.items())
        project = Project.objects.get(user=self.request.user, project_id=self.kwargs['_project_id'])
        queryset = TTSData.objects.filter(project=project)
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
    def download(self, request, **kwargs):
        instance = self.get_object()
        size = os.path.getsize(instance.path)
        mime_type, _ = mimetypes.guess_type(instance.path)
        with open(instance.path, 'rb') as f:
            res = HttpResponse(f.read(), content_type=mime_type)
            res['Content-Disposition'] = "attachment; filename=%s.mp3" % str(instance.data_id)
            res['Content-Length'] = size
            return res
