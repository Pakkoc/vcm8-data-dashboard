"""
profiles 테이블 구조 확인 및 필요한 컬럼 추가
"""
import os
import sys
import django
from django.db import connection

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()


def check_and_fix_table():
    """테이블 구조 확인 및 수정"""
    with connection.cursor() as cursor:
        # 1. 현재 테이블 구조 확인
        print("=" * 60)
        print("현재 profiles 테이블 구조:")
        print("=" * 60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'profiles'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()
        existing_columns = set()

        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            existing_columns.add(col[0])

        print()

        # 2. 필요한 컬럼 확인 및 추가
        required_columns = {
            'id': 'uuid',
            'role': 'varchar(20)',
            'username': 'varchar(100)',
            'email': 'varchar(254)',  # Django EmailField의 기본 길이
            'created_at': 'timestamp with time zone'
        }

        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))

        if missing_columns:
            print("=" * 60)
            print("누락된 컬럼 추가 중:")
            print("=" * 60)

            for col_name, col_type in missing_columns:
                print(f"  - {col_name} ({col_type}) 추가 중...")

                if col_name == 'role':
                    # role은 기본값이 필요
                    cursor.execute(f"""
                        ALTER TABLE profiles
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                        DEFAULT 'general';
                    """)
                elif col_name == 'created_at':
                    # created_at은 기본값으로 현재 시간
                    cursor.execute(f"""
                        ALTER TABLE profiles
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                        DEFAULT CURRENT_TIMESTAMP;
                    """)
                else:
                    # 나머지는 NULL 허용
                    cursor.execute(f"""
                        ALTER TABLE profiles
                        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                        NULL;
                    """)

                print(f"  ✅ {col_name} 추가 완료")

            print()
        else:
            print("✅ 모든 필수 컬럼이 이미 존재합니다.")
            print()

        # 3. 마이그레이션 히스토리에 기록 (fake migrate)
        print("=" * 60)
        print("마이그레이션 히스토리 업데이트 중...")
        print("=" * 60)
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('users', '0001_initial', CURRENT_TIMESTAMP)
            ON CONFLICT DO NOTHING;
        """)
        print("✅ 마이그레이션 히스토리 업데이트 완료")
        print()

        # 4. 최종 테이블 구조 확인
        print("=" * 60)
        print("최종 profiles 테이블 구조:")
        print("=" * 60)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'profiles'
            ORDER BY ordinal_position;
        """)

        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")

        print()
        print("=" * 60)
        print("✅ 테이블 구조 확인 및 수정 완료!")
        print("=" * 60)


if __name__ == '__main__':
    try:
        check_and_fix_table()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
