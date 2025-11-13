import pytest
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from apps.users.models import Profile, UserRole


@pytest.mark.django_db
class TestLoginAPI:
    """로그인 API 테스트"""

    @pytest.fixture
    def api_client(self):
        """API 클라이언트 fixture"""
        return APIClient()

    @patch('apps.users.views.supabase')
    def test_login_success(self, mock_supabase, api_client):
        """로그인 성공 케이스"""
        # Arrange
        mock_auth_response = MagicMock()
        mock_auth_response.user = MagicMock()
        mock_auth_response.user.id = 'test-user-id'
        mock_auth_response.user.email = 'test@example.com'
        mock_auth_response.session = MagicMock()
        mock_auth_response.session.access_token = 'mock-access-token'
        mock_auth_response.session.refresh_token = 'mock-refresh-token'

        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        # Act
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'validpass123'
        })

        # Assert
        assert response.status_code == 200
        assert 'access_token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == 'test@example.com'

    @patch('apps.users.views.supabase')
    def test_login_invalid_credentials(self, mock_supabase, api_client):
        """잘못된 자격 증명으로 로그인 실패"""
        # Arrange
        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

        # Act
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })

        # Assert
        assert response.status_code == 500
        assert 'message' in response.data

    def test_login_missing_email(self, api_client):
        """이메일 누락 시 400 에러"""
        # Act
        response = api_client.post('/api/v1/auth/login/', {
            'password': 'validpass123'
        })

        # Assert
        assert response.status_code == 400
        assert 'email' in response.data

    def test_login_invalid_email_format(self, api_client):
        """잘못된 이메일 형식으로 400 에러"""
        # Act
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'invalid-email',
            'password': 'validpass123'
        })

        # Assert
        assert response.status_code == 400
        assert 'email' in response.data

    def test_login_short_password(self, api_client):
        """6자 미만 비밀번호로 400 에러"""
        # Act
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': '12345'
        })

        # Assert
        assert response.status_code == 400
        assert 'password' in response.data
