from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
import logging

from apps.users.permissions import IsAuthenticatedViaSupabase
from .services.summary_generator import DashboardSummaryService
from .serializers import (
    DashboardSummarySerializer,
    CollegeSerializer, DepartmentSerializer, StudentSerializer,
    DepartmentKPISerializer, PublicationSerializer,
    ResearchProjectSerializer, ProjectExpenseSerializer
)
from .models import (
    College, Department, Student, DepartmentKPI,
    Publication, ResearchProject, ProjectExpense
)

logger = logging.getLogger(__name__)


# ============= CRUD ViewSets =============

class CollegeViewSet(viewsets.ModelViewSet):
    """단과대학 CRUD API"""
    queryset = College.objects.all().order_by('-created_at')
    serializer_class = CollegeSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class DepartmentViewSet(viewsets.ModelViewSet):
    """학과 CRUD API"""
    queryset = Department.objects.select_related('college').all().order_by('-created_at')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class StudentViewSet(viewsets.ModelViewSet):
    """학생 CRUD API"""
    queryset = Student.objects.select_related('department__college').all().order_by('-created_at')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class DepartmentKPIViewSet(viewsets.ModelViewSet):
    """학과 KPI CRUD API"""
    queryset = DepartmentKPI.objects.select_related('department').all().order_by('-evaluation_year', '-created_at')
    serializer_class = DepartmentKPISerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class PublicationViewSet(viewsets.ModelViewSet):
    """논문 CRUD API"""
    queryset = Publication.objects.select_related('department').all().order_by('-publication_date')
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class ResearchProjectViewSet(viewsets.ModelViewSet):
    """연구과제 CRUD API"""
    queryset = ResearchProject.objects.select_related('department').all().order_by('-created_at')
    serializer_class = ResearchProjectSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


class ProjectExpenseViewSet(viewsets.ModelViewSet):
    """과제집행내역 CRUD API"""
    queryset = ProjectExpense.objects.select_related('project__department').all().order_by('-execution_date')
    serializer_class = ProjectExpenseSerializer
    permission_classes = [IsAuthenticatedViaSupabase]


# ============= Dashboard Views =============

class DashboardSummaryView(APIView):
    """대시보드 요약 데이터 조회 API"""

    permission_classes = [IsAuthenticatedViaSupabase]

    def get(self, request):
        """
        대시보드 요약 데이터 반환

        Returns:
            HTTP 200 OK: 대시보드 데이터
            HTTP 401 Unauthorized: 인증 실패
            HTTP 500 Internal Server Error: 서버 오류
        """
        try:
            service = DashboardSummaryService()
            summary_data = service.generate_dashboard_summary()

            serializer = DashboardSummarySerializer(data=summary_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Dashboard summary generation failed: {str(e)}", exc_info=True)

            return Response(
                {'error': '데이터를 불러오는 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
