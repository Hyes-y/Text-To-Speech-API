from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Project, TTSData
from .serializers import ProjectSerializer, TTSDataSerializer


class ProjectViewSet(ModelViewSet):
    """ 프로젝트 CRUD ViewSet """
    # permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'

    def get_queryset(self):
        # queryset = Project.objects.filter(user=self.request.user)
        # test
        queryset = Project.objects.all()
        print(self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TTSDataViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    serializer_class = TTSDataSerializer
    # pagination_class =

    def get_queryset(self):
        # queryset = TTSData.objects.filter(project=self.kwargs['project_id'])
        # test
        queryset = TTSData.objects.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(project=self.kwargs['project_id'])
