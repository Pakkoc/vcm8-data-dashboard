import pytest
from rest_framework.test import APIClient
from apps.users.models import Profile, UserRole
import uuid


@pytest.fixture
def admin_profile():
    """테스트용 관리자 프로필"""
    profile = Profile.objects.create(
        role=UserRole.ADMIN,
        username='Test Admin',
        email='admin@test.com'
    )
    yield profile
    # Cleanup
    profile.delete()


@pytest.fixture
def general_profile():
    """테스트용 일반 사용자 프로필"""
    profile = Profile.objects.create(
        role=UserRole.GENERAL,
        username='Test User',
        email='user@test.com'
    )
    yield profile
    # Cleanup
    profile.delete()


@pytest.fixture
def authenticated_client(general_profile):
    """인증된 API 클라이언트"""
    client = APIClient()
    # 프로필을 request.user로 설정 (미들웨어 대신)
    client.force_authenticate(user=None)
    # 프로필을 직접 할당
    from unittest.mock import Mock
    mock_request = Mock()
    mock_request.profile = general_profile
    client.handler._force_user = mock_request
    return client
