from typing import Optional
from apps.core.repositories import BaseRepository
from .models import Profile, UserRole
import uuid


class ProfileRepository(BaseRepository[Profile]):
    """Profile 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(Profile)

    def get_by_id(self, user_id: uuid.UUID) -> Optional[Profile]:
        """
        사용자 ID로 프로필 조회

        Args:
            user_id: 사용자 ID (UUID)

        Returns:
            Profile 객체 또는 None
        """
        try:
            return self.model_class.objects.get(id=user_id)
        except self.model_class.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[Profile]:
        """
        이메일로 프로필 조회

        Args:
            email: 사용자 이메일

        Returns:
            Profile 객체 또는 None
        """
        try:
            return self.model_class.objects.get(email=email)
        except self.model_class.DoesNotExist:
            return None

    def create_profile(
        self,
        user_id: uuid.UUID,
        role: str,
        username: str = None,
        email: str = None
    ) -> Profile:
        """
        새로운 프로필 생성

        Args:
            user_id: Supabase Auth 사용자 ID
            role: 사용자 역할 (admin 또는 general)
            username: 사용자 이름 (선택)
            email: 이메일 (선택)

        Returns:
            생성된 Profile 객체
        """
        return self.model_class.objects.create(
            id=user_id,
            role=role,
            username=username,
            email=email
        )
