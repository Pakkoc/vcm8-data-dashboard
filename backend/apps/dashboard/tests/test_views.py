import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import Mock, patch

from apps.dashboard.services.summary_generator import DashboardSummaryService


@pytest.mark.django_db
class TestDashboardSummaryView:
    """대시보드 요약 API 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/v1/dashboard/summary/'

    def test_dashboard_summary_requires_authentication(self):
        """인증 없이 접근 시 401 응답"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch.object(DashboardSummaryService, 'generate_dashboard_summary')
    def test_dashboard_summary_with_empty_data(
        self, mock_generate, authenticated_client
    ):
        """데이터가 없을 때 is_empty=True 반환"""
        # Mock: 빈 데이터 반환
        mock_generate.return_value = {'is_empty': True}

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_empty'] is True

    @patch.object(DashboardSummaryService, 'generate_dashboard_summary')
    def test_dashboard_summary_with_data(self, mock_generate, authenticated_client):
        """데이터가 있을 때 정상 응답"""
        # Mock: 정상 데이터 반환
        mock_generate.return_value = {
            'is_empty': False,
            'performance_by_department': [
                {
                    'department_name': '컴퓨터공학과',
                    'college_name': '공과대학',
                    'student_count': 120,
                    'publication_count': 15,
                    'project_count': 8,
                    'total_funding': 800000000,
                }
            ],
            'publications_by_year': [{'year': 2023, 'count': 50}],
            'students_by_status': [{'status': '재학', 'count': 450}],
            'budget_execution': {
                'total_budget': 1600000000,
                'executed_amount': 1283500000,
                'pending_amount': 165000000,
                'execution_rate': 80.22,
            },
        }

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_empty'] is False
        assert 'performance_by_department' in response.data
        assert 'publications_by_year' in response.data
        assert 'students_by_status' in response.data
        assert 'budget_execution' in response.data

    @patch.object(DashboardSummaryService, 'generate_dashboard_summary')
    def test_dashboard_summary_performance_data_structure(
        self, mock_generate, authenticated_client
    ):
        """학과별 성과 데이터 구조 검증"""
        # Mock: 학과별 성과 데이터
        mock_generate.return_value = {
            'is_empty': False,
            'performance_by_department': [
                {
                    'department_name': '컴퓨터공학과',
                    'college_name': '공과대학',
                    'student_count': 120,
                    'publication_count': 15,
                    'project_count': 8,
                    'total_funding': 800000000,
                }
            ],
            'publications_by_year': [],
            'students_by_status': [],
            'budget_execution': {},
        }

        response = authenticated_client.get(self.url)

        performance = response.data['performance_by_department']
        assert len(performance) > 0
        assert 'department_name' in performance[0]
        assert 'student_count' in performance[0]
        assert 'publication_count' in performance[0]

    @patch.object(DashboardSummaryService, 'generate_dashboard_summary')
    def test_dashboard_summary_handles_service_error(
        self, mock_generate, authenticated_client
    ):
        """Service 에러 발생 시 500 응답"""
        # Mock: 에러 발생
        mock_generate.side_effect = Exception("Database connection failed")

        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

    def test_dashboard_summary_method_not_allowed(self, authenticated_client):
        """POST 요청 시 405 응답"""
        response = authenticated_client.post(self.url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
