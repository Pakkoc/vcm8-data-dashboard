import pytest
from apps.users.models import Profile, UserRole
from apps.users.repositories import ProfileRepository


@pytest.mark.django_db
class TestProfileRepository:
    """ProfileRepository 단위 테스트"""

    def test_get_by_id_existing_user(self):
        """존재하는 사용자 ID로 프로필 조회 성공"""
        # Arrange
        profile = Profile.objects.create(
            role=UserRole.ADMIN,
            username='테스트 관리자',
            email='test@example.com'
        )
        repo = ProfileRepository()

        # Act
        result = repo.get_by_id(profile.id)

        # Assert
        assert result is not None
        assert result.id == profile.id
        assert result.role == UserRole.ADMIN
        assert result.username == '테스트 관리자'
        assert result.email == 'test@example.com'

    def test_get_by_id_non_existing_user(self):
        """존재하지 않는 사용자 ID로 조회 시 None 반환"""
        # Arrange
        import uuid
        repo = ProfileRepository()
        non_existing_id = uuid.uuid4()

        # Act
        result = repo.get_by_id(non_existing_id)

        # Assert
        assert result is None

    def test_create_profile_success(self):
        """새로운 프로필 생성 성공"""
        # Arrange
        import uuid
        repo = ProfileRepository()
        user_id = uuid.uuid4()

        # Act
        profile = repo.create_profile(
            user_id=user_id,
            role=UserRole.GENERAL,
            username='일반 사용자',
            email='general@example.com'
        )

        # Assert
        assert profile.id == user_id
        assert profile.role == UserRole.GENERAL
        assert profile.username == '일반 사용자'
        assert profile.email == 'general@example.com'
        assert Profile.objects.filter(id=user_id).exists()

    def test_get_by_email_existing_user(self):
        """이메일로 프로필 조회 성공"""
        # Arrange
        profile = Profile.objects.create(
            role=UserRole.ADMIN,
            username='테스트',
            email='test@example.com'
        )
        repo = ProfileRepository()

        # Act
        result = repo.get_by_email('test@example.com')

        # Assert
        assert result is not None
        assert result.email == 'test@example.com'
        assert result.id == profile.id

    def test_get_by_email_non_existing_user(self):
        """존재하지 않는 이메일로 조회 시 None 반환"""
        # Arrange
        repo = ProfileRepository()

        # Act
        result = repo.get_by_email('nonexisting@example.com')

        # Assert
        assert result is None
