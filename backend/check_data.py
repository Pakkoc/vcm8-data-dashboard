"""
데이터베이스 데이터 확인 스크립트
"""
import os
import sys
import django

# Django 설정 로드
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

from apps.dashboard.models import (
    College, Department, Student, DepartmentKPI,
    Publication, ResearchProject, ProjectExpense
)


def check_database():
    """데이터베이스 데이터 확인"""
    print("=" * 60)
    print("데이터베이스 데이터 확인")
    print("=" * 60)

    tables = [
        ('단과대학 (College)', College),
        ('학과 (Department)', Department),
        ('학생 (Student)', Student),
        ('학과 KPI (DepartmentKPI)', DepartmentKPI),
        ('논문 (Publication)', Publication),
        ('연구 프로젝트 (ResearchProject)', ResearchProject),
        ('프로젝트 지출 (ProjectExpense)', ProjectExpense),
    ]

    total_records = 0

    for table_name, model in tables:
        count = model.objects.count()
        total_records += count
        status = "✅" if count > 0 else "❌"
        print(f"\n{status} {table_name}: {count}개")

        # 처음 3개 레코드 미리보기
        if count > 0:
            records = model.objects.all()[:3]
            for i, record in enumerate(records, 1):
                print(f"   {i}. {record}")

    print("\n" + "=" * 60)
    print(f"총 레코드 수: {total_records}개")
    print("=" * 60)

    if total_records == 0:
        print("\n⚠️  데이터베이스가 비어있습니다!")
        print("데이터 업로드 API 로그를 확인해주세요.")
    else:
        print("\n✅ 데이터가 정상적으로 저장되었습니다.")


if __name__ == '__main__':
    check_database()
