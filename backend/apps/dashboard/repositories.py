from typing import List, Dict, Optional
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear
from apps.core.repositories import BaseRepository
from .models import (
    College,
    Department,
    Student,
    DepartmentKPI,
    Publication,
    ResearchProject,
    ProjectExpense,
    ProjectStatus,
)


class CollegeRepository(BaseRepository[College]):
    def __init__(self):
        super().__init__(College)

    def get_or_create_by_name(self, name: str) -> College:
        """이름으로 조회하거나 생성"""
        college, created = self.model_class.objects.get_or_create(name=name)
        return college


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self):
        super().__init__(Department)

    def get_or_create_by_college_and_name(self, college: College, name: str) -> Department:
        """단과대학과 이름으로 조회하거나 생성"""
        department, created = self.model_class.objects.get_or_create(
            college=college, name=name
        )
        return department

    def get_by_name(self, name: str) -> Optional[Department]:
        """이름으로 조회"""
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None


class StudentRepository(BaseRepository[Student]):
    """학생 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(Student)

    def count_by_department(self, department_id: int) -> int:
        """특정 학과의 학생 수 조회"""
        return self.model_class.objects.filter(department_id=department_id).count()

    def count_by_status(self) -> Dict[str, int]:
        """학적 상태별 학생 수 집계"""
        result = self.model_class.objects.values('status').annotate(count=Count('id'))
        return {item['status']: item['count'] for item in result}

    def count_by_department_and_status(self, department_id: int, status: str) -> int:
        """특정 학과의 특정 학적 상태 학생 수"""
        return self.model_class.objects.filter(
            department_id=department_id, status=status
        ).count()


class DepartmentKPIRepository(BaseRepository[DepartmentKPI]):
    """학과 KPI 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(DepartmentKPI)

    def get_latest_by_department(self, department_id: int) -> Optional[DepartmentKPI]:
        """특정 학과의 최신 KPI"""
        return (
            self.model_class.objects.filter(department_id=department_id)
            .order_by('-evaluation_year')
            .first()
        )


class PublicationRepository(BaseRepository[Publication]):
    """논문 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(Publication)

    def count_by_year(self) -> List[Dict]:
        """연도별 논문 수 집계"""
        return list(
            self.model_class.objects.annotate(year=ExtractYear('publication_date'))
            .values('year')
            .annotate(count=Count('id'))
            .order_by('year')
        )

    def count_by_department(self, department_id: int) -> int:
        """특정 학과의 논문 수 조회"""
        return self.model_class.objects.filter(department_id=department_id).count()

    def get_by_department_and_year(
        self, department_id: int, year: int
    ) -> List[Publication]:
        """특정 학과의 특정 연도 논문"""
        return list(
            self.model_class.objects.filter(
                department_id=department_id, publication_date__year=year
            )
        )


class ResearchProjectRepository(BaseRepository[ResearchProject]):
    """연구 과제 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(ResearchProject)

    def count_by_department(self, department_id: int) -> int:
        """특정 학과의 연구 과제 수"""
        return self.model_class.objects.filter(department_id=department_id).count()

    def get_total_funding_by_department(self, department_id: int) -> int:
        """특정 학과의 총 연구비"""
        result = self.model_class.objects.filter(department_id=department_id).aggregate(
            total=Sum('total_funding_amount')
        )
        return result['total'] or 0


class ProjectExpenseRepository(BaseRepository[ProjectExpense]):
    """연구 과제 집행 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(ProjectExpense)

    def sum_by_status(self, status: str) -> int:
        """특정 상태의 총 집행 금액"""
        result = self.model_class.objects.filter(status=status).aggregate(
            total=Sum('amount')
        )
        return result['total'] or 0

    def calculate_execution_rate(self) -> float:
        """전체 예산 집행률 계산"""
        # 총 예산
        total_budget = ResearchProject.objects.aggregate(total=Sum('total_funding_amount'))[
            'total'
        ] or 0

        # 집행 완료 금액
        executed_amount = self.sum_by_status(ProjectStatus.COMPLETED)

        if total_budget == 0:
            return 0.0
        return round((executed_amount / total_budget) * 100, 2)

    def get_by_project(self, project_id: int) -> List[ProjectExpense]:
        """특정 과제의 집행 내역"""
        return list(
            self.model_class.objects.filter(project_id=project_id).order_by(
                'execution_date'
            )
        )

    def sum_by_project(self, project_id: int) -> int:
        """특정 과제의 총 집행 금액"""
        result = self.model_class.objects.filter(project_id=project_id).aggregate(
            total=Sum('amount')
        )
        return result['total'] or 0
