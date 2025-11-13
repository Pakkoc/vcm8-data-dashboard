"""
관리자 권한 업데이트 스크립트
"""
import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.users.models import Profile


def update_admin_role():
    """admin@test.com 사용자를 관리자로 업데이트"""
    print("=" * 60)
    print("관리자 권한 업데이트")
    print("=" * 60)

    try:
        # admin@test.com 프로필 조회
        profile = Profile.objects.get(email='admin@test.com')

        print(f"\n현재 정보:")
        print(f"   - Email: {profile.email}")
        print(f"   - Role: {profile.role}")

        # role을 admin으로 업데이트
        profile.role = 'admin'
        profile.save()

        print(f"\n✅ 업데이트 완료!")
        print(f"   - Email: {profile.email}")
        print(f"   - Role: {profile.role}")

        print(f"\n이제 admin@test.com으로 로그인하면 '데이터 관리' 메뉴가 표시됩니다.")

    except Profile.DoesNotExist:
        print("\n❌ admin@test.com 프로필이 존재하지 않습니다.")
        print("\n다음 명령어로 프로필을 먼저 생성하세요:")
        print("   python create_test_user.py")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    update_admin_role()
