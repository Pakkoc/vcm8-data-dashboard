from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardSummaryView,
    CollegeViewSet, DepartmentViewSet, StudentViewSet,
    DepartmentKPIViewSet, PublicationViewSet,
    ResearchProjectViewSet, ProjectExpenseViewSet
)

app_name = 'dashboard'

# REST Framework Router 설정
router = DefaultRouter()
router.register(r'colleges', CollegeViewSet, basename='college')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'kpis', DepartmentKPIViewSet, basename='kpi')
router.register(r'publications', PublicationViewSet, basename='publication')
router.register(r'projects', ResearchProjectViewSet, basename='project')
router.register(r'expenses', ProjectExpenseViewSet, basename='expense')

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('', include(router.urls)),
]
