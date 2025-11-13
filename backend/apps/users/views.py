from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import LoginSerializer, ProfileSerializer
from .repositories import ProfileRepository
from .permissions import IsAuthenticatedViaSupabase
from supabase import create_client, Client
from django.conf import settings
import os

# Supabase 클라이언트 생성
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Supabase 클라이언트가 존재하는 경우에만 초기화
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None


class LoginView(APIView):
    """
    사용자 로그인 API

    POST /api/v1/auth/login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. 입력 데이터 검증
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            # 2. Supabase Auth를 통한 인증
            if supabase is None:
                print("❌ Supabase 클라이언트가 초기화되지 않았습니다.")
                print(f"   SUPABASE_URL: {SUPABASE_URL}")
                print(f"   SUPABASE_KEY: {'설정됨' if SUPABASE_KEY else '없음'}")
                return Response(
                    {
                        "message": "인증 서비스가 구성되지 않았습니다.",
                        "code": "SERVER_ERROR"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            print(f"🔐 로그인 시도: {email}")
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user:
                print(f"❌ 로그인 실패: 사용자 없음")
                return Response(
                    {
                        "message": "아이디 또는 비밀번호가 일치하지 않습니다.",
                        "code": "INVALID_CREDENTIALS"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            print(f"✅ 로그인 성공: {auth_response.user.id}")
            # 3. 응답 데이터 구성
            return Response({
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": auth_response.user.email
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # 4. 예외 처리
            print(f"❌ 로그인 예외 발생: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {
                    "message": f"서버 오류: {str(e)}",
                    "code": "SERVER_ERROR"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileView(APIView):
    """
    사용자 프로필 조회 API

    GET /api/v1/auth/profile/
    """
    permission_classes = [IsAuthenticatedViaSupabase]

    def get(self, request):
        try:
            # 미들웨어에서 검증된 사용자 정보 사용
            if not getattr(request, 'is_authenticated', False):
                return Response(
                    {
                        "message": "인증 정보가 없습니다.",
                        "code": "UNAUTHORIZED"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            profile = getattr(request, 'user_profile', None)

            if not profile:
                return Response(
                    {
                        "message": "사용자 권한 정보를 불러올 수 없습니다.",
                        "code": "ROLE_NOT_FOUND"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serializer를 통해 응답 데이터 직렬화
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "message": "프로필 조회 중 오류가 발생했습니다.",
                    "code": "SERVER_ERROR"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    """
    사용자 로그아웃 API

    POST /api/v1/auth/logout/
    """
    permission_classes = [IsAuthenticatedViaSupabase]

    def post(self, request):
        try:
            # Supabase Auth 로그아웃 처리
            if supabase:
                supabase.auth.sign_out()

            return Response(
                {"message": "로그아웃되었습니다."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "message": "로그아웃 중 오류가 발생했습니다.",
                    "code": "SERVER_ERROR"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
