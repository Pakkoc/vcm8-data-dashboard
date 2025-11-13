"""
테스트 사용자 생성 스크립트

사용법:
1. Supabase Dashboard에서 사용자를 먼저 생성하세요:
   - Email: admin@test.com
   - Password: test1234
   - Auto Confirm User: 체크

2. 생성된 사용자의 UUID를 복사하세요

3. 이 스크립트를 실행하세요:
   python create_test_user.py

4. 프롬프트에 UUID를 입력하세요
"""

import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.users.models import Profile


def create_admin_user():
    print("=" * 60)
    print("테스트 관리자 사용자 생성")
    print("=" * 60)
    print()
    print("먼저 Supabase Dashboard에서 다음 사용자를 생성했는지 확인하세요:")
    print("  - Email: admin@test.com")
    print("  - Password: test1234")
    print("  - Auto Confirm User: 체크")
    print()

    user_id = input("생성된 사용자의 UUID를 입력하세요: ").strip()

    if not user_id:
        print("❌ UUID가 비어있습니다.")
        return

    # 이미 존재하는지 확인
    if Profile.objects.filter(user_id=user_id).exists():
        print(f"⚠️  이미 존재하는 사용자입니다: {user_id}")
        return

    # Profile 생성
    profile = Profile.objects.create(
        user_id=user_id,
        email='admin@test.com',
        role='admin'
    )

    print()
    print("✅ 관리자 사용자 생성 완료!")
    print(f"   - User ID: {profile.user_id}")
    print(f"   - Email: {profile.email}")
    print(f"   - Role: {profile.role}")
    print()
    print("이제 로그인할 수 있습니다:")
    print("   - Email: admin@test.com")
    print("   - Password: test1234")


def create_regular_user():
    print("=" * 60)
    print("테스트 일반 사용자 생성")
    print("=" * 60)
    print()
    print("먼저 Supabase Dashboard에서 다음 사용자를 생성했는지 확인하세요:")
    print("  - Email: user@test.com")
    print("  - Password: test1234")
    print("  - Auto Confirm User: 체크")
    print()

    user_id = input("생성된 사용자의 UUID를 입력하세요: ").strip()

    if not user_id:
        print("❌ UUID가 비어있습니다.")
        return

    # 이미 존재하는지 확인
    if Profile.objects.filter(user_id=user_id).exists():
        print(f"⚠️  이미 존재하는 사용자입니다: {user_id}")
        return

    # Profile 생성
    profile = Profile.objects.create(
        user_id=user_id,
        email='user@test.com',
        role='user'
    )

    print()
    print("✅ 일반 사용자 생성 완료!")
    print(f"   - User ID: {profile.user_id}")
    print(f"   - Email: {profile.email}")
    print(f"   - Role: {profile.role}")
    print()
    print("이제 로그인할 수 있습니다:")
    print("   - Email: user@test.com")
    print("   - Password: test1234")


def list_users():
    print("=" * 60)
    print("등록된 사용자 목록")
    print("=" * 60)

    profiles = Profile.objects.all()

    if not profiles:
        print("등록된 사용자가 없습니다.")
        return

    for profile in profiles:
        print(f"\n📧 {profile.email}")
        print(f"   - User ID: {profile.user_id}")
        print(f"   - Role: {profile.role}")
        print(f"   - Created: {profile.created_at}")


def main():
    while True:
        print("\n" + "=" * 60)
        print("테스트 사용자 관리")
        print("=" * 60)
        print("1. 관리자 사용자 생성 (admin@test.com)")
        print("2. 일반 사용자 생성 (user@test.com)")
        print("3. 사용자 목록 보기")
        print("4. 종료")
        print()

        choice = input("선택하세요 (1-4): ").strip()

        if choice == '1':
            create_admin_user()
        elif choice == '2':
            create_regular_user()
        elif choice == '3':
            list_users()
        elif choice == '4':
            print("\n종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-4 사이의 숫자를 입력하세요.")


if __name__ == '__main__':
    main()
