from typing import List, Dict
from django.db.models import Count, Sum

from apps.dashboard.repositories import (
    StudentRepository,
    PublicationRepository,
    DepartmentKPIRepository,
    ProjectExpenseRepository,
    ResearchProjectRepository,
    DepartmentRepository,
)
from apps.dashboard.models import ProjectStatus


class DashboardSummaryService:
    """대시보드 요약 데이터 생성"""

    def __init__(self):
        self.student_repo = StudentRepository()
        self.publication_repo = PublicationRepository()
        self.kpi_repo = DepartmentKPIRepository()
        self.expense_repo = ProjectExpenseRepository()
        self.project_repo = ResearchProjectRepository()
        self.department_repo = DepartmentRepository()

    def generate_dashboard_summary(self) -> dict:
        """
        대시보드 전체 데이터 생성

        Returns:
            {
                'is_empty': bool,
                'performance_by_department': list,
                'publications_by_year': list,
                'students_by_status': list,
                'budget_execution': dict
            }
        """
        # 데이터 존재 여부 확인
        if self._is_data_empty():
            return {'is_empty': True}

        return {
            'is_empty': False,
            'performance_by_department': self._get_performance_by_department(),
            'publications_by_year': self._get_publications_by_year(),
            'students_by_status': self._get_students_by_status(),
            'budget_execution': self._get_budget_execution(),
        }

    def _is_data_empty(self) -> bool:
        """데이터베이스에 데이터가 있는지 확인"""
        return self.student_repo.count() == 0 and self.publication_repo.count() == 0

    def _get_performance_by_department(self) -> List[dict]:
        """학과별 종합 실적 (막대 그래프용)"""
        departments = self.department_repo.get_all()
        performance_data = []

        for dept in departments[:10]:  # 상위 10개 학과만
            student_count = self.student_repo.count_by_department(dept.id)
            publication_count = self.publication_repo.count_by_department(dept.id)
            project_count = self.project_repo.count_by_department(dept.id)
            total_funding = self.project_repo.get_total_funding_by_department(dept.id)

            performance_data.append(
                {
                    'department_name': dept.name,
                    'college_name': dept.college.name,
                    'student_count': student_count,
                    'publication_count': publication_count,
                    'project_count': project_count,
                    'total_funding': total_funding,
                }
            )

        # 학생 수 기준으로 정렬
        performance_data.sort(key=lambda x: x['student_count'], reverse=True)
        return performance_data

    def _get_publications_by_year(self) -> List[dict]:
        """연도별 논문 수 추이 (라인 차트용)"""
        year_data = self.publication_repo.count_by_year()

        # 형식 변환
        return [{'year': int(item['year']), 'count': item['count']} for item in year_data]

    def _get_students_by_status(self) -> List[dict]:
        """학적 상태별 학생 수 (파이 차트용)"""
        status_counts = self.student_repo.count_by_status()

        return [
            {'status': status, 'count': count} for status, count in status_counts.items()
        ]

    def _get_budget_execution(self) -> dict:
        """예산 집행률 (게이지 차트용)"""
        # 총 예산
        from apps.dashboard.models import ResearchProject

        total_budget_result = ResearchProject.objects.aggregate(total=Sum('total_funding_amount'))
        total_budget = total_budget_result['total'] or 0

        # 집행 완료 금액
        executed_amount = self.expense_repo.sum_by_status(ProjectStatus.COMPLETED)

        # 처리중 금액
        pending_amount = self.expense_repo.sum_by_status(ProjectStatus.PROCESSING)

        # 집행률 계산
        execution_rate = 0.0
        if total_budget > 0:
            execution_rate = round((executed_amount / total_budget) * 100, 2)

        return {
            'total_budget': total_budget,
            'executed_amount': executed_amount,
            'pending_amount': pending_amount,
            'execution_rate': execution_rate,
        }
