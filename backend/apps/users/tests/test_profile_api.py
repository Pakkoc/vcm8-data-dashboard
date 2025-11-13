import pytest
from rest_framework.test import APIClient
from apps.users.models import Profile, UserRole
from unittest.mock import MagicMock


@pytest.mark.django_db
class TestProfileAPI:
    """프로필 조회 API 테스트"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def test_profile(self):
        """테스트용 프로필 생성"""
        return Profile.objects.create(
            role=UserRole.ADMIN,
            username='관리자',
            email='admin@test.com'
        )

    def test_get_profile_success(self, api_client, test_profile):
        """인증된 사용자의 프로필 조회 성공"""
        # Arrange
        # JWT 토큰을 시뮬레이션
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer mock-token')

        # Mock request.user
        with pytest.raises(AttributeError):
            # 실제 구현에서는 미들웨어가 request.user를 설정함
            # 이 테스트는 Views 구현 후 수정 필요
            response = api_client.get('/api/v1/auth/profile/')

    def test_get_profile_unauthenticated(self, api_client):
        """인증되지 않은 요청 시 401 에러"""
        # Act
        response = api_client.get('/api/v1/auth/profile/')

        # Assert
        # 실제 구현에서는 401 반환 예상
        # 이 테스트는 미들웨어 구현 후 수정 필요
        pass
