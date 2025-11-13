from rest_framework import serializers
from .models import (
    College, Department, Student, DepartmentKPI,
    Publication, ResearchProject, ProjectExpense
)


# ============= CRUD Serializers =============

class CollegeSerializer(serializers.ModelSerializer):
    """단과대학 Serializer"""
    class Meta:
        model = College
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class DepartmentSerializer(serializers.ModelSerializer):
    """학과 Serializer"""
    college_name = serializers.CharField(source='college.name', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'college', 'college_name', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    """학생 Serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    college_name = serializers.CharField(source='department.college.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id_number', 'name', 'department', 'department_name',
            'college_name', 'grade', 'program_level', 'status', 'gender',
            'admission_year', 'advisor_name', 'email', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DepartmentKPISerializer(serializers.ModelSerializer):
    """학과 KPI Serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = DepartmentKPI
        fields = [
            'id', 'department', 'department_name', 'evaluation_year',
            'employment_rate', 'full_time_faculty_count', 'visiting_faculty_count',
            'tech_transfer_income', 'international_conferences_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PublicationSerializer(serializers.ModelSerializer):
    """논문 Serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Publication
        fields = [
            'id', 'publication_id_str', 'publication_date', 'department',
            'department_name', 'title', 'primary_author', 'contributing_authors',
            'journal_name', 'journal_rank', 'impact_factor', 'is_project_linked',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ResearchProjectSerializer(serializers.ModelSerializer):
    """연구과제 Serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ResearchProject
        fields = [
            'id', 'project_number', 'name', 'principal_investigator',
            'department', 'department_name', 'funding_agency',
            'total_funding_amount', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectExpenseSerializer(serializers.ModelSerializer):
    """과제집행내역 Serializer"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_number = serializers.CharField(source='project.project_number', read_only=True)

    class Meta:
        model = ProjectExpense
        fields = [
            'id', 'execution_id', 'project', 'project_name', 'project_number',
            'execution_date', 'item', 'amount', 'status', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ============= Dashboard Serializers =============

class DashboardSummarySerializer(serializers.Serializer):
    """대시보드 요약 응답 Serializer"""

    is_empty = serializers.BooleanField()
    performance_by_department = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    publications_by_year = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    students_by_status = serializers.ListField(
        child=serializers.DictField(), required=False
    )
    budget_execution = serializers.DictField(required=False)


class FileUploadSerializer(serializers.Serializer):
    """파일 업로드 요청 Serializer"""

    file = serializers.FileField()

    def validate_file(self, value):
        """파일 확장자 검증"""
        if not value.name.endswith(('.xlsx', '.xls', '.csv')):
            raise serializers.ValidationError(
                "엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드할 수 있습니다."
            )

        # 파일 크기 검증 (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"파일 크기는 {max_size // (1024*1024)}MB를 초과할 수 없습니다."
            )

        return value


class ChartDataSerializer(serializers.Serializer):
    """차트 데이터 응답 Serializer"""

    name = serializers.CharField()
    value = serializers.IntegerField()


class DepartmentPerformanceSerializer(serializers.Serializer):
    """학과별 성과 데이터 Serializer"""

    department_name = serializers.CharField()
    college_name = serializers.CharField()
    student_count = serializers.IntegerField()
    publication_count = serializers.IntegerField()
    project_count = serializers.IntegerField()
    total_funding = serializers.IntegerField()


class BudgetExecutionSerializer(serializers.Serializer):
    """예산 집행 데이터 Serializer"""

    total_budget = serializers.IntegerField()
    executed_amount = serializers.IntegerField()
    pending_amount = serializers.IntegerField()
    execution_rate = serializers.FloatField()


class UploadResultSerializer(serializers.Serializer):
    """데이터 업로드 결과 Serializer"""

    success = serializers.BooleanField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
