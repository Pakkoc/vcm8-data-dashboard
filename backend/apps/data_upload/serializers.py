"""
Serializers for data upload app
"""
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """파일 업로드 요청 Serializer"""

    file = serializers.FileField()

    def validate_file(self, value):
        """파일 확장자 및 크기 검증"""

        # 파일 이름 검증
        if not value.name:
            raise serializers.ValidationError("파일 이름이 올바르지 않습니다.")

        # 확장자 검증
        allowed_extensions = ['.xlsx', '.xls']
        file_extension = '.' + value.name.lower().split('.')[-1]

        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                "엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다."
            )

        # 파일 크기 검증 (10MB)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"파일 크기가 너무 큽니다. 최대 {max_size // (1024 * 1024)}MB까지 업로드 가능합니다."
            )

        return value
