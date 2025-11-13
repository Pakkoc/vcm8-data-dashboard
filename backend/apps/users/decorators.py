from functools import wraps
from django.http import JsonResponse
from .models import UserRole


def login_required(view_func):
    """로그인 필수 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """관리자 권한 필수 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'is_authenticated', False):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        user_profile = getattr(request, 'user_profile', None)
        if not user_profile or user_profile.role != UserRole.ADMIN:
            return JsonResponse({'error': 'Admin access required'}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper
