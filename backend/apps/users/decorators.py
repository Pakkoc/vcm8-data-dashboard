from functools import wraps
from django.http import JsonResponse
from .models import UserRole


def login_required(view_func):
    """로그인 필수 데코레이터 (함수 기반 뷰용)"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """관리자 권한 필수 데코레이터 (클래스 기반 뷰의 메서드용)"""
    @wraps(view_func)
    def wrapper(self_or_request, *args, **kwargs):
        # 클래스 기반 뷰의 메서드인 경우 첫 번째 인자가 self, 두 번째가 request
        # 함수 기반 뷰인 경우 첫 번째 인자가 request
        if hasattr(self_or_request, 'request'):
            # self인 경우 (클래스 기반 뷰)
            request = args[0] if args else kwargs.get('request')
            view_self = self_or_request
        else:
            # request인 경우 (함수 기반 뷰)
            request = self_or_request
            view_self = None

        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        user_profile = getattr(request, 'user_profile', None)
        if not user_profile or user_profile.role != UserRole.ADMIN:
            return JsonResponse({'error': 'Admin access required'}, status=403)

        if view_self:
            return view_func(view_self, request, *args[1:], **kwargs)
        else:
            return view_func(request, *args, **kwargs)
    return wrapper
