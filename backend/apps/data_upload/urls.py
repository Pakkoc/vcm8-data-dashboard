"""
URL routing for data upload app
"""
from django.urls import path
from .views import DataUploadView

urlpatterns = [
    path('', DataUploadView.as_view(), name='data-upload'),
]
