"""
URL configuration for dashboard_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
    path('api/v1/data-upload/', include('apps.data_upload.urls')),

    # Catch-all pattern: 모든 non-API 요청을 React SPA로 라우팅
    # API 경로가 아닌 모든 경로는 index.html을 반환
    re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html'), name='frontend'),
]
