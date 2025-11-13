"""
여러 CSV 파일 동시 Import 테스트 스크립트
"""
import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.dashboard.services.excel_importer import ExcelImportService


def test_multiple_csv_import():
    """여러 CSV 파일 동시 Import 테스트"""
    print("=" * 60)
    print("여러 CSV 파일 동시 Import 테스트")
    print("=" * 60)

    # CSV 파일 경로
    csv_files = [
        '../docs/input_data/student_roster.csv',
        '../docs/input_data/department_kpi.csv',
        '../docs/input_data/publication_list.csv',
        '../docs/input_data/research_project_data.csv',
    ]

    file_paths = []
    for csv_file in csv_files:
        file_path = os.path.join(os.path.dirname(__file__), csv_file)
        if os.path.exists(file_path):
            file_paths.append(file_path)
            print(f"✓ 파일 발견: {os.path.basename(file_path)}")
        else:
            print(f"✗ 파일 없음: {file_path}")

    if not file_paths:
        print("\n❌ 업로드할 파일이 없습니다.")
        return

    print(f"\n총 {len(file_paths)}개 파일을 동시에 업로드합니다...")
    print("="*60)

    service = ExcelImportService()

    try:
        result = service.import_from_multiple_files(file_paths)
        print(f"\n{'='*60}")
        print("✅ 배치 Import 성공!")
        print(f"{'='*60}")
        print(f"단과대학: {result['colleges']}개")
        print(f"학과: {result['departments']}개")
        print(f"학생: {result['students']}명")
        print(f"학과 KPI: {result['department_kpis']}개")
        print(f"논문: {result['publications']}개")
        print(f"연구 프로젝트: {result['research_projects']}개")
        print(f"프로젝트 지출: {result['project_expenses']}개")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ 배치 Import 실패: {type(e).__name__}")
        print(f"{'='*60}")
        print(f"에러 메시지: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_multiple_csv_import()
