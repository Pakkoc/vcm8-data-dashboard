from rest_framework import serializers


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
