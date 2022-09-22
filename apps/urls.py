from django.urls import path, include

urlpatterns = [
    path('account/', include('apps.account.urls')),
    path('projects/', include('apps.project.urls')),
]
