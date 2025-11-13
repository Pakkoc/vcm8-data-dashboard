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

from apps.users.permissions import IsAdmin
from apps.dashboard.services.excel_importer import ExcelImportService
from .serializers import FileUploadSerializer, MultipleFileUploadSerializer

logger = logging.getLogger(__name__)


class DataUploadView(APIView):
    """
    데이터 업로드 API

    관리자가 엑셀 파일을 업로드하여 시스템 데이터를 갱신한다.
    """

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdmin]

    def post(self, request):
        # 여러 파일 업로드인지 단일 파일 업로드인지 확인
        is_multiple = 'files' in request.FILES or request.data.get('files')

        if is_multiple:
            return self._handle_multiple_files(request)
        else:
            return self._handle_single_file(request)

    def _handle_single_file(self, request):
        """단일 파일 업로드 처리"""
        # 1. 요청 검증
        serializer = FileUploadSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(f"파일 검증 실패: {serializer.errors}")
            return Response(
                {
                    'status': 'error',
                    'message': '파일 형식이 올바르지 않습니다.',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = serializer.validated_data['file']
        logger.info(f"파일 업로드 시작: {uploaded_file.name}")

        try:
            # 2. 임시 파일 저장
            temp_file_path = self._save_temp_file(uploaded_file)
            logger.info(f"임시 파일 저장 완료: {temp_file_path}")

            # 3. ExcelImportService 초기화 및 실행
            excel_service = ExcelImportService()

            # 4. 데이터 Import 실행 (트랜잭션 내부에서 처리)
            logger.info("데이터 Import 시작...")
            result = excel_service.import_from_excel(temp_file_path)
            logger.info(f"데이터 Import 완료: {result}")

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

            # 관리자에게만 상세 오류 표시
            user_profile = getattr(request, 'user_profile', None)
            show_details = user_profile and user_profile.role == 'admin'

            return Response(
                {
                    'status': 'error',
                    'message': '데이터 처리 중 오류가 발생했습니다. 관리자에게 문의하세요.',
                    'details': str(e) if show_details else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _handle_multiple_files(self, request):
        """여러 파일 동시 업로드 처리"""
        # 1. 파일 목록 추출
        files_list = request.FILES.getlist('files')

        if not files_list:
            return Response(
                {
                    'status': 'error',
                    'message': '업로드할 파일이 없습니다.',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. 요청 검증
        serializer = MultipleFileUploadSerializer(data={'files': files_list})

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.error(f"파일 검증 실패: {serializer.errors}")
            return Response(
                {
                    'status': 'error',
                    'message': '파일 형식이 올바르지 않습니다.',
                    'details': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_files = serializer.validated_data['files']
        logger.info(f"여러 파일 업로드 시작: {[f.name for f in uploaded_files]}")

        temp_file_paths = []

        try:
            # 3. 모든 파일을 임시 저장
            for uploaded_file in uploaded_files:
                temp_file_path = self._save_temp_file(uploaded_file)
                temp_file_paths.append(temp_file_path)
                logger.info(f"임시 파일 저장 완료: {temp_file_path}")

            # 4. ExcelImportService 초기화 및 배치 실행
            excel_service = ExcelImportService()

            # 5. 배치 Import 실행 (모든 파일을 한 번에 처리)
            logger.info("배치 데이터 Import 시작...")
            result = excel_service.import_from_multiple_files(temp_file_paths)
            logger.info(f"배치 데이터 Import 완료: {result}")

            # 6. 임시 파일 삭제
            for temp_file_path in temp_file_paths:
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

            # 7. 성공 응답
            return Response(
                {
                    'status': 'success',
                    'message': f'{len(uploaded_files)}개 파일이 성공적으로 업로드되었습니다.',
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

            # 임시 파일 정리
            for temp_file_path in temp_file_paths:
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

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
            logger.error(f"Unexpected error during multiple file upload: {str(e)}", exc_info=True)

            # 임시 파일 정리
            for temp_file_path in temp_file_paths:
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

            # 관리자에게만 상세 오류 표시
            user_profile = getattr(request, 'user_profile', None)
            show_details = user_profile and user_profile.role == 'admin'

            return Response(
                {
                    'status': 'error',
                    'message': '데이터 처리 중 오류가 발생했습니다. 관리자에게 문의하세요.',
                    'details': str(e) if show_details else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _save_temp_file(self, uploaded_file: UploadedFile) -> str:
        """업로드된 파일을 임시 디렉토리에 저장"""
        # 임시 파일 생성 (원본 파일명 기반)
        temp_dir = tempfile.gettempdir()
        # 원본 파일명 유지 (안전한 파일명으로 변환)
        import re
        safe_filename = re.sub(r'[^\w\s.-]', '', uploaded_file.name)
        temp_file_path = os.path.join(temp_dir, safe_filename)

        # 파일이 이미 존재하면 고유한 이름 생성
        if os.path.exists(temp_file_path):
            base_name = os.path.splitext(safe_filename)[0]
            extension = os.path.splitext(safe_filename)[1]
            import time
            temp_file_path = os.path.join(temp_dir, f"{base_name}_{int(time.time())}{extension}")

        temp_file = open(temp_file_path, 'wb')

        # 청크 단위로 파일 쓰기
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

        temp_file.close()
        return temp_file_path
