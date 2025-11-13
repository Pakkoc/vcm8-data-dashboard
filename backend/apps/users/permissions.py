"""
커스텀 권한 클래스
"""
from rest_framework.permissions import BasePermission


class IsAuthenticatedViaSupabase(BasePermission):
    """
    Supabase 미들웨어를 통해 인증된 사용자만 허용
    """
    def has_permission(self, request, view):
        # 미들웨어에서 설정한 is_authenticated 확인
        return getattr(request, 'is_authenticated', False)


class IsAdmin(BasePermission):
    """
    관리자 권한만 허용
    """
    def has_permission(self, request, view):
        if not getattr(request, 'is_authenticated', False):
            return False

        profile = getattr(request, 'user_profile', None)
        return profile and profile.role == 'admin'
