"""
Test suite for FileUploadSerializer

Following TDD principles:
- Test file validation logic
- Test extension validation
- Test file size validation
"""
import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.data_upload.serializers import FileUploadSerializer


class TestFileUploadSerializer:
    """Test cases for FileUploadSerializer"""

    def test_valid_xlsx_file(self):
        """유효한 .xlsx 파일은 검증을 통과한다"""
        file_content = b'fake excel content'
        file = SimpleUploadedFile(
            'test.xlsx',
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert serializer.is_valid()
        assert 'file' in serializer.validated_data

    def test_valid_xls_file(self):
        """유효한 .xls 파일은 검증을 통과한다"""
        file_content = b'fake excel content'
        file = SimpleUploadedFile(
            'test.xls',
            file_content,
            content_type='application/vnd.ms-excel'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert serializer.is_valid()

    def test_invalid_pdf_file(self):
        """.pdf 파일은 검증에 실패한다"""
        file = SimpleUploadedFile(
            'test.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert '엑셀 파일' in str(serializer.errors['file'])

    def test_invalid_docx_file(self):
        """.docx 파일은 검증에 실패한다"""
        file = SimpleUploadedFile(
            'test.docx',
            b'fake word content',
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_file_size_exceeds_limit(self):
        """10MB 초과 파일은 검증에 실패한다"""
        # 11MB 크기의 파일 시뮬레이션
        large_content = b'a' * (11 * 1024 * 1024)
        file = SimpleUploadedFile(
            'large.xlsx',
            large_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert not serializer.is_valid()
        assert 'file' in serializer.errors
        assert '크기' in str(serializer.errors['file'])

    def test_file_size_within_limit(self):
        """10MB 이하 파일은 검증을 통과한다"""
        # 5MB 크기의 파일
        content = b'a' * (5 * 1024 * 1024)
        file = SimpleUploadedFile(
            'medium.xlsx',
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert serializer.is_valid()

    def test_no_file_provided(self):
        """파일이 제공되지 않으면 검증에 실패한다"""
        serializer = FileUploadSerializer(data={})

        assert not serializer.is_valid()
        assert 'file' in serializer.errors

    def test_empty_filename(self):
        """빈 파일명은 검증에 실패한다"""
        file = SimpleUploadedFile(
            '',
            b'content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        serializer = FileUploadSerializer(data={'file': file})

        # 빈 파일명은 확장자 검증 실패로 이어짐
        assert not serializer.is_valid()
