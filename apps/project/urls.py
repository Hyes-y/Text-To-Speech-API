from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter
from django.urls import include, path
from .views import ProjectViewSet, TTSDataViewSet


router = routers.DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

detail_router = NestedSimpleRouter(router, r'', lookup='project')
detail_router.register(r'data', TTSDataViewSet, basename='project-data')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(detail_router.urls)),
]