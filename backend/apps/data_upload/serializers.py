"""
Serializers for data upload app
"""
from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """파일 업로드 요청 Serializer (단일 파일)"""

    file = serializers.FileField()

    def validate_file(self, value):
        """파일 확장자 및 크기 검증"""

        # 파일 이름 검증
        if not value.name:
            raise serializers.ValidationError("파일 이름이 올바르지 않습니다.")

        # 확장자 검증 (Excel 및 CSV 지원)
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        file_extension = '.' + value.name.lower().split('.')[-1]

        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                "엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드할 수 있습니다."
            )

        # 파일 크기 검증 (10MB)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"파일 크기가 너무 큽니다. 최대 {max_size // (1024 * 1024)}MB까지 업로드 가능합니다."
            )

        return value


class MultipleFileUploadSerializer(serializers.Serializer):
    """여러 파일 업로드 요청 Serializer"""

    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        max_length=10  # 최대 10개 파일
    )

    def validate_files(self, value):
        """각 파일의 확장자 및 크기 검증"""
        allowed_extensions = ['.xlsx', '.xls', '.csv']
        max_size = 10 * 1024 * 1024

        for file in value:
            # 파일 이름 검증
            if not file.name:
                raise serializers.ValidationError("파일 이름이 올바르지 않습니다.")

            # 확장자 검증
            file_extension = '.' + file.name.lower().split('.')[-1]
            if file_extension not in allowed_extensions:
                raise serializers.ValidationError(
                    f"'{file.name}': 엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드할 수 있습니다."
                )

            # 파일 크기 검증
            if file.size > max_size:
                raise serializers.ValidationError(
                    f"'{file.name}': 파일 크기가 너무 큽니다. 최대 {max_size // (1024 * 1024)}MB까지 업로드 가능합니다."
                )

        return value
