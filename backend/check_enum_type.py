"""
user_role ENUM 타입 확인 및 수정
"""
import os
import sys
import django
from django.db import connection

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()


def check_and_fix_enum():
    """ENUM 타입 확인 및 수정"""
    with connection.cursor() as cursor:
        # 1. user_role ENUM 타입 확인
        print("=" * 60)
        print("user_role ENUM 타입 확인:")
        print("=" * 60)

        cursor.execute("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'user_role'
            ORDER BY e.enumsortorder;
        """)

        enum_values = [row[0] for row in cursor.fetchall()]

        if enum_values:
            print("현재 enum 값:")
            for val in enum_values:
                print(f"  - {val}")
            print()
        else:
            print("⚠️  user_role enum이 존재하지 않습니다.")
            print()

        # 2. 필요한 값 확인 및 추가
        required_values = ['admin', 'general']
        missing_values = [val for val in required_values if val not in enum_values]

        if missing_values:
            print("=" * 60)
            print("누락된 enum 값 추가 중:")
            print("=" * 60)

            for val in missing_values:
                print(f"  - '{val}' 추가 중...")
                try:
                    cursor.execute(f"""
                        ALTER TYPE user_role ADD VALUE IF NOT EXISTS '{val}';
                    """)
                    print(f"  ✅ '{val}' 추가 완료")
                except Exception as e:
                    print(f"  ❌ '{val}' 추가 실패: {e}")

            print()

        else:
            print("✅ 모든 필요한 enum 값이 이미 존재합니다.")
            print()

        # 3. 최종 enum 값 확인
        print("=" * 60)
        print("최종 user_role ENUM 값:")
        print("=" * 60)

        cursor.execute("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'user_role'
            ORDER BY e.enumsortorder;
        """)

        for row in cursor.fetchall():
            print(f"  - {row[0]}")

        print()
        print("=" * 60)
        print("✅ ENUM 타입 확인 및 수정 완료!")
        print("=" * 60)


if __name__ == '__main__':
    try:
        check_and_fix_enum()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
