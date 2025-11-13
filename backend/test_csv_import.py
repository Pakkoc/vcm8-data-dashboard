"""
CSV 파일 Import 테스트 스크립트
"""
import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.dashboard.services.excel_importer import ExcelImportService


def test_csv_import():
    """CSV 파일 Import 테스트"""
    print("=" * 60)
    print("CSV 파일 Import 테스트")
    print("=" * 60)

    # CSV 파일 경로
    csv_files = [
        '../docs/input_data/student_roster.csv',
        '../docs/input_data/department_kpi.csv',
        '../docs/input_data/publication_list.csv',
        '../docs/input_data/research_project_data.csv',
    ]

    service = ExcelImportService()

    for csv_file in csv_files:
        file_path = os.path.join(os.path.dirname(__file__), csv_file)

        if not os.path.exists(file_path):
            print(f"\n❌ 파일이 존재하지 않습니다: {file_path}")
            continue

        print(f"\n{'='*60}")
        print(f"파일: {os.path.basename(file_path)}")
        print('='*60)

        try:
            result = service.import_from_excel(file_path)
            print(f"✅ Import 성공!")
            print(f"결과: {result}")

        except Exception as e:
            print(f"❌ Import 실패: {type(e).__name__}")
            print(f"에러 메시지: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("테스트 완료")
    print('='*60)


if __name__ == '__main__':
    test_csv_import()
