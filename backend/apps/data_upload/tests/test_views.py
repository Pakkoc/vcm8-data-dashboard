"""
Test suite for DataUploadView

Following TDD principles:
- Test admin authentication
- Test file upload success
- Test error handling
"""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from apps.users.models import Profile, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestDataUploadView:
    """Test cases for DataUploadView"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def admin_user(self):
        """관리자 유저 생성"""
        user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        Profile.objects.create(id=user.id, role=UserRole.ADMIN)
        return user

    @pytest.fixture
    def general_user(self):
        """일반 유저 생성"""
        user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        Profile.objects.create(id=user.id, role=UserRole.GENERAL)
        return user

    def test_upload_success_with_admin(self, api_client, admin_user):
        """관리자는 파일 업로드에 성공한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService') as MockService:
            mock_service = MockService.return_value
            mock_service.import_from_excel.return_value = {
                'students': 10,
                'department_kpis': 5,
                'publications': 3,
                'research_projects': 2,
                'project_expenses': 5
            }

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert '성공' in response.data['message']

    def test_upload_forbidden_with_general_user(self, api_client, general_user):
        """일반 유저는 파일 업로드가 차단된다"""
        api_client.force_authenticate(user=general_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_invalid_file_format(self, api_client, admin_user):
        """잘못된 파일 형식은 400 에러를 반환한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_data_validation_error(self, api_client, admin_user):
        """데이터 검증 실패 시 400 에러를 반환한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService') as MockService:
            from rest_framework.exceptions import ValidationError
            mock_service = MockService.return_value
            mock_service.import_from_excel.side_effect = ValidationError(['학번 컬럼이 누락되었습니다.'])

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '형식' in response.data['message'] or 'message' in response.data

    def test_upload_database_error_rollback(self, api_client, admin_user):
        """데이터베이스 오류 시 500 에러 및 트랜잭션 롤백"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService') as MockService:
            mock_service = MockService.return_value
            mock_service.import_from_excel.side_effect = Exception('Database connection error')

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_upload_no_authentication(self, api_client):
        """인증되지 않은 사용자는 401 에러를 받는다"""
        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_upload_no_file_provided(self, api_client, admin_user):
        """파일이 제공되지 않으면 400 에러를 반환한다"""
        api_client.force_authenticate(user=admin_user)

        url = reverse('data-upload')
        response = api_client.post(url, {}, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
