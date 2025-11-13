import jwt
from django.conf import settings
from django.http import JsonResponse
from .models import Profile


class SupabaseAuthMiddleware:
    """JWT 토큰 검증 및 사용자 정보 추출"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Authorization 헤더에서 JWT 토큰 추출
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:
                # JWT 토큰 디코드 (Supabase JWT Secret 사용)
                decoded = jwt.decode(
                    token,
                    settings.SUPABASE_SERVICE_KEY,
                    algorithms=['HS256'],
                    options={'verify_aud': False}
                )

                user_id = decoded.get('sub')
                user_email = decoded.get('email')

                # 프로필 조회 또는 생성
                profile, created = Profile.objects.get_or_create(
                    id=user_id,
                    defaults={'email': user_email}
                )

                # request에 사용자 정보 저장
                request.user_profile = profile
                request.is_authenticated = True

            except jwt.ExpiredSignatureError:
                request.is_authenticated = False
                request.user_profile = None
            except jwt.InvalidTokenError:
                request.is_authenticated = False
                request.user_profile = None
            except Exception as e:
                print(f"Auth middleware error: {e}")
                request.is_authenticated = False
                request.user_profile = None
        else:
            request.is_authenticated = False
            request.user_profile = None

        response = self.get_response(request)
        return response
