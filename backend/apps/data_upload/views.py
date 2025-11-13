"""
API views for data upload
"""
import tempfile
import os
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from apps.users.decorators import admin_required
from apps.dashboard.services.excel_importer import ExcelImportService
from .serializers import FileUploadSerializer

logger = logging.getLogger(__name__)


class DataUploadView(APIView):
    """
    데이터 업로드 API

    관리자가 엑셀 파일을 업로드하여 시스템 데이터를 갱신한다.
    """

    parser_classes = (MultiPartParser, FormParser)

    @admin_required
    def post(self, request):
        # 1. 요청 검증
        serializer = FileUploadSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(
                {
                    'status': 'error',
                    'message': '파일 형식이 올바르지 않습니다.',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = serializer.validated_data['file']

        try:
            # 2. 임시 파일 저장
            temp_file_path = self._save_temp_file(uploaded_file)

            # 3. ExcelImportService 초기화 및 실행
            excel_service = ExcelImportService()

            # 4. 데이터 Import 실행 (트랜잭션 내부에서 처리)
            result = excel_service.import_from_excel(temp_file_path)

            # 5. 임시 파일 삭제
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

            # 6. 성공 응답
            return Response(
                {
                    'status': 'success',
                    'message': '데이터가 성공적으로 업로드되었습니다.',
                    'details': {
                        'students': result.get('students', 0),
                        'department_kpis': result.get('department_kpis', 0),
                        'publications': result.get('publications', 0),
                        'research_projects': result.get('research_projects', 0),
                        'project_expenses': result.get('project_expenses', 0)
                    }
                },
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            # 데이터 검증 실패
            error_details = []
            if hasattr(e, 'detail'):
                if isinstance(e.detail, list):
                    error_details = e.detail
                elif isinstance(e.detail, dict):
                    error_details = [str(v) for v in e.detail.values()]
                else:
                    error_details = [str(e.detail)]
            else:
                error_details = [str(e)]

            return Response(
                {
                    'status': 'error',
                    'message': '데이터 형식이 올바르지 않습니다.',
                    'details': error_details
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # 예기치 않은 오류 로깅
            logger.error(f"Unexpected error during data upload: {str(e)}", exc_info=True)

            return Response(
                {
                    'status': 'error',
                    'message': '데이터 처리 중 오류가 발생했습니다. 관리자에게 문의하세요.',
                    'details': str(e) if request.user.is_superuser else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _save_temp_file(self, uploaded_file: UploadedFile) -> str:
        """업로드된 파일을 임시 디렉토리에 저장"""
        # 임시 파일 생성
        temp_dir = tempfile.gettempdir()
        file_extension = os.path.splitext(uploaded_file.name)[1]
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            dir=temp_dir
        )

        # 청크 단위로 파일 쓰기
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name
