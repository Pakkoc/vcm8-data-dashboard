"""
관리자 프로필 확인 스크립트
"""
import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.users.models import Profile


def check_admin_profile():
    """관리자 프로필 확인"""
    print("=" * 60)
    print("관리자 프로필 확인")
    print("=" * 60)

    # admin@test.com 프로필 조회
    try:
        admin_profile = Profile.objects.get(email='admin@test.com')

        print(f"\n✅ 관리자 프로필 발견:")
        print(f"   - ID: {admin_profile.id}")
        print(f"   - Email: {admin_profile.email}")
        print(f"   - Role: {admin_profile.role}")
        print(f"   - Username: {admin_profile.username}")
        print(f"   - Created: {admin_profile.created_at}")

        if admin_profile.role == 'admin':
            print(f"\n✅ 관리자 권한이 정상적으로 설정되어 있습니다!")
        else:
            print(f"\n⚠️  경고: role이 '{admin_profile.role}'입니다. 'admin'으로 변경해야 합니다.")

    except Profile.DoesNotExist:
        print("\n❌ admin@test.com 프로필이 존재하지 않습니다.")
        print("\n다음 명령어로 프로필을 생성하세요:")
        print("   python create_test_user.py")

    print("\n" + "=" * 60)
    print("모든 프로필 목록:")
    print("=" * 60)

    profiles = Profile.objects.all()
    if not profiles:
        print("등록된 프로필이 없습니다.")
    else:
        for profile in profiles:
            print(f"\n📧 {profile.email or '(이메일 없음)'}")
            print(f"   - ID: {profile.id}")
            print(f"   - Role: {profile.role}")
            print(f"   - Username: {profile.username or '(이름 없음)'}")


if __name__ == '__main__':
    check_admin_profile()
