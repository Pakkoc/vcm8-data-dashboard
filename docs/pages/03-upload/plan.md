# 데이터 업로드 페이지 구현 계획

**페이지 ID:** 03-upload
**페이지 이름:** 데이터 업로드 페이지 (Data Upload Page)
**작성일:** 2025-11-13
**작성자:** Development Team
**관련 유스케이스:** UC-002 (엑셀 파일 업로드)

---

## 1. 개요

### 1.1 페이지 목적

관리자가 이카운트 시스템에서 추출한 대학 데이터를 엑셀 파일로 업로드하여 시스템의 모든 데이터를 최신 상태로 갱신하는 페이지입니다. 업로드된 데이터는 메인 대시보드의 차트 및 그래프에 즉시 반영됩니다.

### 1.2 핵심 기능

- 엑셀 파일 선택 및 업로드 (.xlsx, .xls)
- 클라이언트 측 파일 형식 검증
- 서버 측 데이터 스키마 검증
- 업로드 진행 상황 시각화
- 성공/실패 피드백 메시지
- 관리자 권한 검증

### 1.3 참조 문서

- `/docs/PRD.md` - 제품 요구사항 정의서 (섹션 3, 4.2)
- `/docs/userflow.md` - 사용자 플로우 (섹션 2.1)
- `/docs/usecases/02-excel-upload/spec.md` - 엑셀 업로드 유스케이스
- `/docs/database.md` - 데이터베이스 스키마
- `/docs/common-modules.md` - 공통 모듈 (ExcelImportService 등)
- `/docs/input_data/*.csv` - 입력 데이터 형식 샘플

---

## 2. 프론트엔드 구현

### 2.1 컴포넌트 구조

```
/frontend/src/pages/UploadPage/
├── index.jsx                     # 메인 페이지 컴포넌트
├── components/
│   ├── FileUploadArea.jsx        # 파일 선택 영역 (드래그 앤 드롭)
│   ├── FileInfo.jsx              # 선택된 파일 정보 표시
│   ├── UploadButton.jsx          # 업로드 버튼
│   ├── UploadProgressBar.jsx     # 업로드 진행 상황 표시
│   └── FeedbackMessage.jsx       # 성공/실패 메시지
├── hooks/
│   ├── useFileUpload.js          # 파일 업로드 로직 훅
│   └── useFileValidation.js      # 파일 검증 로직 훅
└── UploadPage.test.jsx           # 페이지 통합 테스트
```

### 2.2 페이지 레이아웃 (UploadPage/index.jsx)

**책임:**
- 전체 페이지 레이아웃 관리
- MainLayout으로 헤더 포함
- 하위 컴포넌트 조합
- 관리자 권한 확인

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/index.jsx

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/layout/MainLayout';
import useAuthStore from '../../store/authStore';
import FileUploadArea from './components/FileUploadArea';
import FileInfo from './components/FileInfo';
import UploadButton from './components/UploadButton';
import UploadProgressBar from './components/UploadProgressBar';
import FeedbackMessage from './components/FeedbackMessage';
import useFileUpload from './hooks/useFileUpload';

const UploadPage = () => {
  const { isAdmin } = useAuthStore();
  const navigate = useNavigate();

  const {
    selectedFile,
    isUploading,
    uploadProgress,
    feedbackMessage,
    feedbackType,
    handleFileSelect,
    handleUpload,
    resetState
  } = useFileUpload();

  // 관리자 권한 확인
  useEffect(() => {
    if (!isAdmin()) {
      navigate('/dashboard');
    }
  }, [isAdmin, navigate]);

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">데이터 업로드</h1>

        <div className="bg-white rounded-lg shadow-md p-6">
          {/* 안내 문구 */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-blue-800">
              이카운트에서 추출한 엑셀 파일을 업로드하면 대시보드의 모든 데이터가 갱신됩니다.
            </p>
            <p className="text-sm text-blue-800 mt-1">
              지원 형식: .xlsx, .xls | 최대 크기: 10MB
            </p>
          </div>

          {/* 파일 선택 영역 */}
          <FileUploadArea
            onFileSelect={handleFileSelect}
            disabled={isUploading}
          />

          {/* 선택된 파일 정보 */}
          {selectedFile && (
            <FileInfo
              file={selectedFile}
              onReset={resetState}
            />
          )}

          {/* 업로드 버튼 */}
          <UploadButton
            disabled={!selectedFile || isUploading}
            loading={isUploading}
            onClick={handleUpload}
          />

          {/* 진행률 표시 */}
          {isUploading && (
            <UploadProgressBar progress={uploadProgress} />
          )}

          {/* 피드백 메시지 */}
          {feedbackMessage && (
            <FeedbackMessage
              type={feedbackType}
              message={feedbackMessage}
              onNavigateToDashboard={() => navigate('/dashboard')}
            />
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default UploadPage;
```

**테스트 계획:**
- 관리자가 아닌 경우 대시보드로 리디렉션
- 컴포넌트가 올바른 순서로 렌더링
- 파일 선택 시 상태 업데이트 확인

---

### 2.3 파일 업로드 영역 (FileUploadArea.jsx)

**책임:**
- 파일 선택 버튼 제공
- 드래그 앤 드롭 지원
- 파일 선택 이벤트 처리

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/components/FileUploadArea.jsx

import { useState } from 'react';
import { FiUpload } from 'react-icons/fi';

const FileUploadArea = ({ onFileSelect, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        border-2 border-dashed rounded-lg p-12 text-center
        transition-colors cursor-pointer
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <FiUpload className="mx-auto text-4xl text-gray-400 mb-4" />

      <label className="cursor-pointer">
        <span className="text-blue-600 hover:underline">파일 선택</span>
        <span className="text-gray-600"> 또는 파일을 여기로 드래그하세요</span>
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />
      </label>
    </div>
  );
};

export default FileUploadArea;
```

**테스트 계획:**
- 파일 선택 버튼 클릭 시 파일 다이얼로그 오픈
- 드래그 앤 드롭 시 파일 선택 콜백 호출
- disabled 상태에서 작동 차단
- .xlsx, .xls 이외의 파일은 브라우저 레벨에서 필터링

---

### 2.4 파일 정보 표시 (FileInfo.jsx)

**책임:**
- 선택된 파일명 표시
- 파일 크기 표시
- 파일 선택 취소 버튼

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/components/FileInfo.jsx

import { FiFile, FiX } from 'react-icons/fi';

const FileInfo = ({ file, onReset }) => {
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg flex items-center justify-between">
      <div className="flex items-center gap-3">
        <FiFile className="text-2xl text-blue-600" />
        <div>
          <p className="font-medium text-gray-900">{file.name}</p>
          <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
        </div>
      </div>
      <button
        onClick={onReset}
        className="p-2 hover:bg-gray-200 rounded-full transition-colors"
        title="파일 선택 취소"
      >
        <FiX className="text-xl text-gray-600" />
      </button>
    </div>
  );
};

export default FileInfo;
```

**테스트 계획:**
- 파일명과 크기가 올바르게 표시
- 취소 버튼 클릭 시 onReset 콜백 호출
- 파일 크기 포맷팅 정확성 검증

---

### 2.5 업로드 버튼 (UploadButton.jsx)

**책임:**
- 업로드 액션 트리거
- 로딩 상태 표시
- 버튼 활성화/비활성화 관리

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/components/UploadButton.jsx

import Button from '../../../components/common/Button';

const UploadButton = ({ disabled, loading, onClick }) => {
  return (
    <div className="mt-6">
      <Button
        onClick={onClick}
        disabled={disabled}
        loading={loading}
        variant="primary"
        className="w-full py-3"
      >
        {loading ? '업로드 중...' : '업로드'}
      </Button>
    </div>
  );
};

export default UploadButton;
```

**테스트 계획:**
- 파일이 선택되지 않았을 때 비활성화
- 업로드 중일 때 비활성화 및 로딩 텍스트 표시
- 클릭 시 onClick 콜백 호출

---

### 2.6 진행률 표시 (UploadProgressBar.jsx)

**책임:**
- 업로드 진행률을 시각적으로 표시
- 퍼센트 표시

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/components/UploadProgressBar.jsx

const UploadProgressBar = ({ progress }) => {
  return (
    <div className="mt-4">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>데이터 처리 중...</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default UploadProgressBar;
```

**테스트 계획:**
- progress 값에 따라 프로그레스 바 너비 변경
- 0%와 100% 엣지 케이스 검증

---

### 2.7 피드백 메시지 (FeedbackMessage.jsx)

**책임:**
- 성공/실패 메시지 표시
- 대시보드 이동 버튼 제공 (성공 시)
- 재시도 안내 (실패 시)

**구현 계획:**

```jsx
// /frontend/src/pages/UploadPage/components/FeedbackMessage.jsx

import { FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import Button from '../../../components/common/Button';

const FeedbackMessage = ({ type, message, onNavigateToDashboard }) => {
  const isSuccess = type === 'success';

  return (
    <div
      className={`
        mt-6 p-4 rounded-lg border
        ${isSuccess
          ? 'bg-green-50 border-green-200'
          : 'bg-red-50 border-red-200'
        }
      `}
    >
      <div className="flex items-start gap-3">
        {isSuccess ? (
          <FiCheckCircle className="text-2xl text-green-600 flex-shrink-0" />
        ) : (
          <FiAlertCircle className="text-2xl text-red-600 flex-shrink-0" />
        )}

        <div className="flex-1">
          <p className={`font-medium ${isSuccess ? 'text-green-900' : 'text-red-900'}`}>
            {isSuccess ? '업로드 성공' : '업로드 실패'}
          </p>
          <p className={`text-sm mt-1 ${isSuccess ? 'text-green-800' : 'text-red-800'}`}>
            {message}
          </p>

          {isSuccess && (
            <Button
              onClick={onNavigateToDashboard}
              variant="primary"
              className="mt-3"
            >
              대시보드에서 확인하기
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackMessage;
```

**테스트 계획:**
- success 타입일 때 녹색 스타일 및 대시보드 버튼 표시
- error 타입일 때 빨간색 스타일
- 메시지 내용 정확히 렌더링

---

### 2.8 파일 업로드 훅 (useFileUpload.js)

**책임:**
- 파일 선택 상태 관리
- 클라이언트 측 파일 검증
- API 호출 및 업로드 진행 관리
- 성공/실패 피드백 관리

**구현 계획:**

```javascript
// /frontend/src/pages/UploadPage/hooks/useFileUpload.js

import { useState } from 'react';
import { dataUploadAPI } from '../../../api/dataUploadAPI';
import useFileValidation from './useFileValidation';

const useFileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  const [feedbackType, setFeedbackType] = useState(''); // 'success' | 'error'

  const { validateFile } = useFileValidation();

  const handleFileSelect = (file) => {
    // 클라이언트 측 검증
    const validation = validateFile(file);

    if (!validation.isValid) {
      setFeedbackMessage(validation.errorMessage);
      setFeedbackType('error');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setFeedbackMessage('');
    setFeedbackType('');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setFeedbackMessage('');

    try {
      // 업로드 진행 상황 시뮬레이션
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // API 호출
      const response = await dataUploadAPI.uploadExcel(selectedFile);

      clearInterval(progressInterval);
      setUploadProgress(100);

      // 성공 처리
      setFeedbackMessage(
        response.message || '데이터가 성공적으로 업로드되었습니다.'
      );
      setFeedbackType('success');

    } catch (error) {
      // 실패 처리
      let errorMessage = '데이터 처리 중 오류가 발생했습니다.';

      if (error.response) {
        const { status, data } = error.response;

        switch (status) {
          case 400:
            errorMessage = data.message || '데이터 형식이 올바르지 않습니다.';
            if (data.details && Array.isArray(data.details)) {
              errorMessage += '\n' + data.details.join('\n');
            }
            break;
          case 403:
            errorMessage = '이 기능은 관리자만 사용할 수 있습니다.';
            break;
          case 413:
            errorMessage = '파일 크기가 너무 큽니다. 파일 크기를 줄이거나 데이터를 분할하여 다시 시도해주세요.';
            break;
          case 500:
            errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
            break;
          default:
            errorMessage = data.message || errorMessage;
        }
      } else if (error.request) {
        errorMessage = '서버에 연결할 수 없습니다. 네트워크 연결을 확인한 후 다시 시도해주세요.';
      }

      setFeedbackMessage(errorMessage);
      setFeedbackType('error');

    } finally {
      setIsUploading(false);
    }
  };

  const resetState = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setFeedbackMessage('');
    setFeedbackType('');
  };

  return {
    selectedFile,
    isUploading,
    uploadProgress,
    feedbackMessage,
    feedbackType,
    handleFileSelect,
    handleUpload,
    resetState
  };
};

export default useFileUpload;
```

**테스트 계획:**
- 파일 선택 시 검증 로직 실행
- 유효하지 않은 파일 선택 시 에러 메시지 설정
- API 호출 성공 시 success 피드백
- API 호출 실패 시 적절한 에러 메시지
- 네트워크 오류 시 연결 오류 메시지
- 진행률 업데이트 확인

---

### 2.9 파일 검증 훅 (useFileValidation.js)

**책임:**
- 파일 확장자 검증
- 파일 크기 검증
- 파일 존재 여부 검증

**구현 계획:**

```javascript
// /frontend/src/pages/UploadPage/hooks/useFileValidation.js

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_EXTENSIONS = ['.xlsx', '.xls'];

const useFileValidation = () => {
  const validateFile = (file) => {
    // 파일 존재 여부
    if (!file) {
      return {
        isValid: false,
        errorMessage: '파일을 선택해주세요.'
      };
    }

    // 파일 확장자 검증
    const fileName = file.name.toLowerCase();
    const isValidExtension = ALLOWED_EXTENSIONS.some(ext =>
      fileName.endsWith(ext)
    );

    if (!isValidExtension) {
      return {
        isValid: false,
        errorMessage: '엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다.'
      };
    }

    // 파일 크기 검증
    if (file.size > MAX_FILE_SIZE) {
      return {
        isValid: false,
        errorMessage: '파일 크기가 10MB를 초과할 수 없습니다.'
      };
    }

    return {
      isValid: true,
      errorMessage: ''
    };
  };

  return { validateFile };
};

export default useFileValidation;
```

**테스트 계획:**
- null 파일 처리
- .xlsx, .xls 파일은 통과
- .pdf, .docx 등 다른 확장자는 실패
- 10MB 초과 파일은 실패
- 유효한 파일은 isValid: true 반환

---

## 3. 백엔드 구현

### 3.1 API 엔드포인트 구조

```
/backend/apps/data_upload/
├── __init__.py
├── views.py                      # API 뷰 함수
├── serializers.py                # 요청/응답 Serializer
├── urls.py                       # URL 라우팅
├── exceptions.py                 # 커스텀 예외
└── tests/
    ├── test_views.py             # 뷰 테스트
    ├── test_serializers.py       # Serializer 테스트
    └── test_integration.py       # 통합 테스트
```

### 3.2 API 엔드포인트 (views.py)

**엔드포인트:** `POST /api/v1/data-upload/`

**책임:**
- Multipart/form-data 파일 수신
- 파일 임시 저장
- ExcelImportService 호출
- 예외 처리 및 응답 생성

**구현 계획:**

```python
# /backend/apps/data_upload/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.users.decorators import admin_required
from apps.dashboard.services.excel_importer import ExcelImportService
from apps.dashboard.repositories import (
    CollegeRepository,
    DepartmentRepository,
    StudentRepository,
    DepartmentKPIRepository,
    PublicationRepository,
    ResearchProjectRepository,
    ProjectExpenseRepository
)
from .serializers import FileUploadSerializer
from .exceptions import (
    InvalidFileFormatError,
    FileParsingError,
    DataValidationError
)

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
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']

        try:
            # 2. 임시 파일 저장
            temp_file_path = self._save_temp_file(uploaded_file)

            # 3. ExcelImportService 초기화
            excel_service = self._init_excel_service()

            # 4. 데이터 Import 실행 (트랜잭션 내부에서 처리)
            result = excel_service.import_from_excel(temp_file_path)

            # 5. 성공 응답
            return Response({
                'status': 'success',
                'message': '데이터가 성공적으로 업로드되었습니다.',
                'details': {
                    'students': result['students'],
                    'department_kpis': result['department_kpis'],
                    'publications': result['publications'],
                    'research_projects': result['projects']['projects_count'],
                    'project_expenses': result['projects']['expenses_count']
                }
            }, status=status.HTTP_200_OK)

        except InvalidFileFormatError as e:
            return Response({
                'status': 'error',
                'message': '파일 형식이 올바르지 않습니다.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except FileParsingError as e:
            return Response({
                'status': 'error',
                'message': '엑셀 파일을 읽을 수 없습니다. 파일이 손상되었거나 올바른 형식이 아닙니다.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except DataValidationError as e:
            return Response({
                'status': 'error',
                'message': '데이터 형식이 올바르지 않습니다.',
                'details': e.errors if hasattr(e, 'errors') else [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # 예기치 않은 오류 로깅
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error during data upload: {str(e)}", exc_info=True)

            return Response({
                'status': 'error',
                'message': '데이터 처리 중 오류가 발생했습니다. 관리자에게 문의하세요.',
                'details': str(e) if request.user.is_superuser else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _save_temp_file(self, uploaded_file: UploadedFile) -> str:
        """업로드된 파일을 임시 디렉토리에 저장"""
        import tempfile
        import os

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

    def _init_excel_service(self) -> ExcelImportService:
        """ExcelImportService 초기화 (의존성 주입)"""
        return ExcelImportService(
            college_repo=CollegeRepository(),
            department_repo=DepartmentRepository(),
            student_repo=StudentRepository(),
            kpi_repo=DepartmentKPIRepository(),
            publication_repo=PublicationRepository(),
            project_repo=ResearchProjectRepository(),
            expense_repo=ProjectExpenseRepository()
        )
```

**테스트 계획:**
- 정상 파일 업로드 성공 (200 OK)
- 잘못된 파일 형식 (400 Bad Request)
- 파일 파싱 실패 (400 Bad Request)
- 데이터 검증 실패 (400 Bad Request)
- 관리자 권한 없음 (403 Forbidden)
- 데이터베이스 오류 시 트랜잭션 롤백 (500 Internal Server Error)

---

### 3.3 Serializer (serializers.py)

**책임:**
- 파일 업로드 요청 검증
- 파일 확장자 검증

**구현 계획:**

```python
# /backend/apps/data_upload/serializers.py

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
        file_extension = value.name.lower().split('.')[-1]

        if f'.{file_extension}' not in allowed_extensions:
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
```

**테스트 계획:**
- .xlsx, .xls 파일은 검증 통과
- .pdf, .docx 파일은 ValidationError
- 10MB 초과 파일은 ValidationError
- 빈 파일명 처리

---

### 3.4 커스텀 예외 (exceptions.py)

**구현 계획:**

```python
# /backend/apps/data_upload/exceptions.py

class InvalidFileFormatError(Exception):
    """파일 형식이 올바르지 않을 때 발생"""
    pass

class FileParsingError(Exception):
    """파일 파싱 중 오류 발생 시"""
    pass

class DataValidationError(Exception):
    """데이터 검증 실패 시 발생"""

    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        super().__init__(str(self.errors))
```

---

### 3.5 URL 라우팅 (urls.py)

```python
# /backend/apps/data_upload/urls.py

from django.urls import path
from .views import DataUploadView

urlpatterns = [
    path('', DataUploadView.as_view(), name='data-upload'),
]
```

```python
# /backend/dashboard_project/urls.py

from django.urls import path, include

urlpatterns = [
    # ... 기존 URL 패턴
    path('api/v1/data-upload/', include('apps.data_upload.urls')),
]
```

---

### 3.6 ExcelImportService 강화

**공통 모듈에 이미 구현된 ExcelImportService를 확장/수정합니다.**

**수정 사항:**

1. **파일 읽기 메소드 강화**

```python
# /backend/apps/dashboard/services/excel_importer.py

def _read_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
    """
    엑셀 파일을 읽어 DataFrame 딕셔너리로 반환

    Raises:
        FileParsingError: 파일을 읽을 수 없을 때
        InvalidFileFormatError: 파일 형식이 올바르지 않을 때
    """
    try:
        # 엑셀 파일의 모든 시트를 읽기
        excel_file = pd.ExcelFile(file_path)

        # 예상 시트명 정의
        expected_sheets = {
            'student_roster': 'students',
            'department_kpi': 'kpis',
            'publication_list': 'publications',
            'research_project_data': 'projects'
        }

        dataframes = {}

        for sheet_name, key in expected_sheets.items():
            if sheet_name in excel_file.sheet_names:
                dataframes[key] = pd.read_excel(excel_file, sheet_name=sheet_name)
            else:
                # 시트가 없을 경우 대안 처리
                # 1개 시트만 있는 경우, 해당 시트를 읽어서 판단
                if len(excel_file.sheet_names) == 1:
                    dataframes[key] = pd.read_excel(excel_file, sheet_name=0)
                else:
                    raise InvalidFileFormatError(
                        f"필수 시트 '{sheet_name}'가 없습니다."
                    )

        return dataframes

    except pd.errors.ParserError as e:
        raise FileParsingError(f"엑셀 파일 파싱 중 오류 발생: {str(e)}")
    except Exception as e:
        raise FileParsingError(f"파일을 읽을 수 없습니다: {str(e)}")
```

2. **데이터 검증 강화**

```python
def _validate_data(self, dataframes: Dict[str, pd.DataFrame]) -> None:
    """모든 데이터프레임 검증"""
    errors = []

    # 학생 명단 검증
    if 'students' in dataframes:
        try:
            self.validator.validate_columns(
                dataframes['students'],
                self.validator.STUDENT_REQUIRED_COLUMNS,
                'student_roster'
            )
            self.validator.validate_not_empty(
                dataframes['students'],
                'student_roster'
            )
        except ValidationError as e:
            errors.append(str(e))

    # 학과 KPI 검증
    if 'kpis' in dataframes:
        try:
            self.validator.validate_columns(
                dataframes['kpis'],
                self.validator.DEPARTMENT_KPI_REQUIRED_COLUMNS,
                'department_kpi'
            )
            self.validator.validate_not_empty(
                dataframes['kpis'],
                'department_kpi'
            )
        except ValidationError as e:
            errors.append(str(e))

    # 논문 목록 검증
    if 'publications' in dataframes:
        try:
            self.validator.validate_columns(
                dataframes['publications'],
                self.validator.PUBLICATION_REQUIRED_COLUMNS,
                'publication_list'
            )
            self.validator.validate_not_empty(
                dataframes['publications'],
                'publication_list'
            )
        except ValidationError as e:
            errors.append(str(e))

    # 연구 과제 검증
    if 'projects' in dataframes:
        try:
            self.validator.validate_columns(
                dataframes['projects'],
                self.validator.RESEARCH_PROJECT_REQUIRED_COLUMNS,
                'research_project_data'
            )
            self.validator.validate_not_empty(
                dataframes['projects'],
                'research_project_data'
            )
        except ValidationError as e:
            errors.append(str(e))

    if errors:
        raise DataValidationError(errors)
```

---

## 4. 공통 모듈 활용

### 4.1 사용할 기존 공통 모듈

**백엔드:**
- `ExcelImportService` (apps/dashboard/services/excel_importer.py)
- `DataSchemaValidator` (apps/dashboard/services/validators.py)
- Repository 레이어 (apps/dashboard/repositories.py)
  - CollegeRepository
  - DepartmentRepository
  - StudentRepository
  - DepartmentKPIRepository
  - PublicationRepository
  - ResearchProjectRepository
  - ProjectExpenseRepository
- `admin_required` 데코레이터 (apps/users/decorators.py)

**프론트엔드:**
- `apiClient` (src/api/index.js)
- `dataUploadAPI` (src/api/dataUploadAPI.js)
- `useAuthStore` (src/store/authStore.js)
- `MainLayout` (src/components/layout/MainLayout.jsx)
- `Button` (src/components/common/Button.jsx)

### 4.2 추가로 구현할 공통 컴포넌트

**없음** - 페이지에 필요한 모든 공통 모듈은 이미 구현되어 있습니다.

---

## 5. 에러 핸들링

### 5.1 클라이언트 측 에러 처리

| 에러 유형 | 처리 방법 | 사용자 메시지 |
|-----------|-----------|---------------|
| 잘못된 파일 형식 | 파일 선택 시 즉시 차단 | "엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다." |
| 파일 크기 초과 | 파일 선택 시 즉시 차단 | "파일 크기가 10MB를 초과할 수 없습니다." |
| 네트워크 오류 | Axios catch 블록에서 처리 | "서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요." |

### 5.2 서버 측 에러 처리

| HTTP 상태 코드 | 발생 상황 | 응답 메시지 |
|---------------|-----------|-------------|
| 400 Bad Request | 데이터 스키마 검증 실패 | "데이터 형식이 올바르지 않습니다." + 상세 오류 목록 |
| 400 Bad Request | 파일 파싱 실패 | "엑셀 파일을 읽을 수 없습니다." |
| 400 Bad Request | 빈 파일 | "파일에 처리할 데이터가 없습니다." |
| 403 Forbidden | 관리자 권한 없음 | "이 기능은 관리자만 사용할 수 있습니다." |
| 413 Payload Too Large | 파일 크기 초과 (서버 레벨) | "파일 크기가 너무 큽니다." |
| 500 Internal Server Error | 데이터베이스 오류 등 | "데이터 처리 중 오류가 발생했습니다." |

### 5.3 트랜잭션 롤백 보장

```python
# ExcelImportService의 import_from_excel 메소드는 @transaction.atomic 데코레이터 사용
@transaction.atomic
def import_from_excel(self, file_path: str) -> Dict[str, int]:
    # 모든 데이터베이스 작업이 하나의 트랜잭션으로 묶임
    # 중간에 예외 발생 시 자동 롤백
    pass
```

---

## 6. 테스트 계획

### 6.1 프론트엔드 테스트

#### 6.1.1 단위 테스트 (Component Tests)

**FileUploadArea 테스트:**

```javascript
// /frontend/src/pages/UploadPage/components/FileUploadArea.test.jsx

import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import FileUploadArea from './FileUploadArea';

describe('FileUploadArea', () => {
  it('파일 선택 input이 렌더링된다', () => {
    const onFileSelect = vi.fn();
    render(<FileUploadArea onFileSelect={onFileSelect} />);

    const input = screen.getByRole('textbox', { hidden: true });
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('accept', '.xlsx,.xls');
  });

  it('파일 선택 시 onFileSelect 콜백이 호출된다', () => {
    const onFileSelect = vi.fn();
    render(<FileUploadArea onFileSelect={onFileSelect} />);

    const file = new File(['content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const input = screen.getByRole('textbox', { hidden: true });

    fireEvent.change(input, { target: { files: [file] } });

    expect(onFileSelect).toHaveBeenCalledWith(file);
  });

  it('disabled 상태일 때 파일 선택이 차단된다', () => {
    const onFileSelect = vi.fn();
    render(<FileUploadArea onFileSelect={onFileSelect} disabled />);

    const input = screen.getByRole('textbox', { hidden: true });
    expect(input).toBeDisabled();
  });

  // 드래그 앤 드롭 테스트 추가
});
```

**useFileValidation 테스트:**

```javascript
// /frontend/src/pages/UploadPage/hooks/useFileValidation.test.js

import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import useFileValidation from './useFileValidation';

describe('useFileValidation', () => {
  it('.xlsx 파일은 검증을 통과한다', () => {
    const { result } = renderHook(() => useFileValidation());
    const file = new File(['content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    const validation = result.current.validateFile(file);

    expect(validation.isValid).toBe(true);
    expect(validation.errorMessage).toBe('');
  });

  it('.pdf 파일은 검증에 실패한다', () => {
    const { result } = renderHook(() => useFileValidation());
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

    const validation = result.current.validateFile(file);

    expect(validation.isValid).toBe(false);
    expect(validation.errorMessage).toContain('엑셀 파일');
  });

  it('10MB 초과 파일은 검증에 실패한다', () => {
    const { result } = renderHook(() => useFileValidation());
    const largeContent = new Array(11 * 1024 * 1024).fill('a').join('');
    const file = new File([largeContent], 'large.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    const validation = result.current.validateFile(file);

    expect(validation.isValid).toBe(false);
    expect(validation.errorMessage).toContain('10MB');
  });

  it('null 파일은 검증에 실패한다', () => {
    const { result } = renderHook(() => useFileValidation());

    const validation = result.current.validateFile(null);

    expect(validation.isValid).toBe(false);
  });
});
```

**useFileUpload 테스트:**

```javascript
// /frontend/src/pages/UploadPage/hooks/useFileUpload.test.js

import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import useFileUpload from './useFileUpload';
import { dataUploadAPI } from '../../../api/dataUploadAPI';

vi.mock('../../../api/dataUploadAPI');

describe('useFileUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('유효한 파일 선택 시 상태가 업데이트된다', () => {
    const { result } = renderHook(() => useFileUpload());
    const file = new File(['content'], 'test.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    act(() => {
      result.current.handleFileSelect(file);
    });

    expect(result.current.selectedFile).toBe(file);
    expect(result.current.feedbackMessage).toBe('');
  });

  it('업로드 성공 시 success 피드백이 표시된다', async () => {
    dataUploadAPI.uploadExcel.mockResolvedValue({
      message: '성공적으로 업로드되었습니다.'
    });

    const { result } = renderHook(() => useFileUpload());
    const file = new File(['content'], 'test.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    act(() => {
      result.current.handleFileSelect(file);
    });

    await act(async () => {
      await result.current.handleUpload();
    });

    await waitFor(() => {
      expect(result.current.feedbackType).toBe('success');
      expect(result.current.feedbackMessage).toContain('성공');
      expect(result.current.isUploading).toBe(false);
    });
  });

  it('업로드 실패 시 error 피드백이 표시된다', async () => {
    dataUploadAPI.uploadExcel.mockRejectedValue({
      response: {
        status: 400,
        data: {
          message: '데이터 형식이 올바르지 않습니다.'
        }
      }
    });

    const { result } = renderHook(() => useFileUpload());
    const file = new File(['content'], 'test.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });

    act(() => {
      result.current.handleFileSelect(file);
    });

    await act(async () => {
      await result.current.handleUpload();
    });

    await waitFor(() => {
      expect(result.current.feedbackType).toBe('error');
      expect(result.current.feedbackMessage).toContain('형식');
    });
  });

  // 네트워크 오류, 403, 500 등 추가 테스트
});
```

#### 6.1.2 통합 테스트 (Page Integration Test)

```javascript
// /frontend/src/pages/UploadPage/UploadPage.test.jsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import UploadPage from './index';
import useAuthStore from '../../store/authStore';
import { dataUploadAPI } from '../../api/dataUploadAPI';

vi.mock('../../store/authStore');
vi.mock('../../api/dataUploadAPI');

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('UploadPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.mockReturnValue({
      isAdmin: () => true
    });
  });

  it('페이지가 정상적으로 렌더링된다', () => {
    renderWithRouter(<UploadPage />);

    expect(screen.getByText('데이터 업로드')).toBeInTheDocument();
    expect(screen.getByText(/지원 형식/)).toBeInTheDocument();
  });

  it('관리자가 아닐 경우 대시보드로 리디렉션된다', () => {
    useAuthStore.mockReturnValue({
      isAdmin: () => false
    });

    const mockNavigate = vi.fn();
    vi.mock('react-router-dom', async () => {
      const actual = await vi.importActual('react-router-dom');
      return {
        ...actual,
        useNavigate: () => mockNavigate
      };
    });

    renderWithRouter(<UploadPage />);

    // 리디렉션 로직 검증
  });

  it('파일 업로드 전체 플로우가 정상 작동한다', async () => {
    dataUploadAPI.uploadExcel.mockResolvedValue({
      message: '성공적으로 업로드되었습니다.'
    });

    renderWithRouter(<UploadPage />);

    // 1. 파일 선택
    const file = new File(['content'], 'test.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const input = screen.getByRole('textbox', { hidden: true });
    fireEvent.change(input, { target: { files: [file] } });

    // 2. 파일 정보 확인
    await waitFor(() => {
      expect(screen.getByText('test.xlsx')).toBeInTheDocument();
    });

    // 3. 업로드 버튼 클릭
    const uploadButton = screen.getByText('업로드');
    fireEvent.click(uploadButton);

    // 4. 성공 메시지 확인
    await waitFor(() => {
      expect(screen.getByText(/성공/)).toBeInTheDocument();
      expect(screen.getByText('대시보드에서 확인하기')).toBeInTheDocument();
    });
  });
});
```

---

### 6.2 백엔드 테스트

#### 6.2.1 단위 테스트 (Unit Tests)

**Serializer 테스트:**

```python
# /backend/apps/data_upload/tests/test_serializers.py

import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.data_upload.serializers import FileUploadSerializer

class TestFileUploadSerializer:

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

    def test_invalid_pdf_file(self):
        """.pdf 파일은 검증에 실패한다"""
        file = SimpleUploadedFile(
            'test.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )

        serializer = FileUploadSerializer(data={'file': file})

        assert not serializer.is_valid()
        assert '엑셀 파일' in str(serializer.errors)

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
        assert '크기' in str(serializer.errors)
```

**View 테스트:**

```python
# /backend/apps/data_upload/tests/test_views.py

import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import Profile, UserRole

@pytest.mark.django_db
class TestDataUploadView:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def admin_user(self, django_user_model):
        """관리자 유저 생성"""
        user = django_user_model.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        Profile.objects.create(id=user.id, role=UserRole.ADMIN)
        return user

    @pytest.fixture
    def general_user(self, django_user_model):
        """일반 유저 생성"""
        user = django_user_model.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        Profile.objects.create(id=user.id, role=UserRole.GENERAL)
        return user

    def test_upload_success_with_admin(self, api_client, admin_user):
        """관리자는 파일 업로드에 성공한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService.import_from_excel') as mock_import:
            mock_import.return_value = {
                'students': 10,
                'department_kpis': 5,
                'publications': 3,
                'projects': {'projects_count': 2, 'expenses_count': 5}
            }

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert '성공' in response.data['message']

    def test_upload_forbidden_with_general_user(self, api_client, general_user):
        """일반 유저는 파일 업로드가 차단된다"""
        api_client.force_authenticate(user=general_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_invalid_file_format(self, api_client, admin_user):
        """잘못된 파일 형식은 400 에러를 반환한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_data_validation_error(self, api_client, admin_user):
        """데이터 검증 실패 시 400 에러를 반환한다"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService.import_from_excel') as mock_import:
            from apps.data_upload.exceptions import DataValidationError
            mock_import.side_effect = DataValidationError(['학번 컬럼이 누락되었습니다.'])

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '형식' in response.data['message']

    def test_upload_database_error_rollback(self, api_client, admin_user):
        """데이터베이스 오류 시 500 에러 및 트랜잭션 롤백"""
        api_client.force_authenticate(user=admin_user)

        file = SimpleUploadedFile(
            'test.xlsx',
            b'fake excel content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        with patch('apps.data_upload.views.ExcelImportService.import_from_excel') as mock_import:
            mock_import.side_effect = Exception('Database connection error')

            url = reverse('data-upload')
            response = api_client.post(url, {'file': file}, format='multipart')

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
```

#### 6.2.2 통합 테스트 (Integration Tests)

```python
# /backend/apps/data_upload/tests/test_integration.py

import pytest
import os
import pandas as pd
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import Profile, UserRole
from apps.dashboard.models import (
    College, Department, Student, DepartmentKPI,
    Publication, ResearchProject, ProjectExpense
)

@pytest.mark.django_db
class TestDataUploadIntegration:
    """실제 엑셀 파일 업로드부터 데이터베이스 저장까지 전체 플로우 테스트"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def admin_user(self, django_user_model):
        user = django_user_model.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        Profile.objects.create(id=user.id, role=UserRole.ADMIN)
        return user

    @pytest.fixture
    def sample_excel_file(self, tmp_path):
        """샘플 엑셀 파일 생성"""
        excel_path = tmp_path / "test_data.xlsx"

        # 학생 명단 데이터
        students_df = pd.DataFrame({
            '학번': ['20201101', '20211205'],
            '이름': ['김유진', '박지훈'],
            '단과대학': ['공과대학', '공과대학'],
            '학과': ['컴퓨터공학과', '전자공학과'],
            '학년': [4, 3],
            '과정구분': ['학사', '학사'],
            '학적상태': ['재학', '재학'],
            '성별': ['여', '남'],
            '입학년도': [2020, 2021],
            '지도교수': ['이서연', '김민준'],
            '이메일': ['yjkim@univ.ac.kr', 'jhpark@univ.ac.kr']
        })

        # 엑셀 파일로 저장
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            students_df.to_excel(writer, sheet_name='student_roster', index=False)

        return excel_path

    def test_full_upload_flow(self, api_client, admin_user, sample_excel_file):
        """전체 업로드 플로우 통합 테스트"""
        api_client.force_authenticate(user=admin_user)

        # 1. 기존 데이터 확인
        assert College.objects.count() == 0
        assert Student.objects.count() == 0

        # 2. 파일 업로드
        with open(sample_excel_file, 'rb') as f:
            file_content = f.read()

        file = SimpleUploadedFile(
            'test.xlsx',
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        url = reverse('data-upload')
        response = api_client.post(url, {'file': file}, format='multipart')

        # 3. 응답 검증
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'

        # 4. 데이터베이스 검증
        assert College.objects.count() == 1
        assert Department.objects.count() == 2
        assert Student.objects.count() == 2

        # 5. 데이터 내용 검증
        student = Student.objects.get(student_id_number='20201101')
        assert student.name == '김유진'
        assert student.department.name == '컴퓨터공학과'
        assert student.department.college.name == '공과대학'
```

---

### 6.3 E2E 테스트 (선택 사항)

**Playwright를 사용한 E2E 테스트:**

```javascript
// /frontend/e2e/upload-page.spec.js

import { test, expect } from '@playwright/test';

test.describe('데이터 업로드 페이지 E2E', () => {
  test.beforeEach(async ({ page }) => {
    // 관리자로 로그인
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin@test.com');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');

    // 업로드 페이지로 이동
    await page.goto('/upload');
  });

  test('파일 업로드 성공 시나리오', async ({ page }) => {
    // 파일 선택
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-data/sample.xlsx');

    // 파일 정보 확인
    await expect(page.locator('text=sample.xlsx')).toBeVisible();

    // 업로드 버튼 클릭
    await page.click('button:has-text("업로드")');

    // 로딩 표시 확인
    await expect(page.locator('text=업로드 중')).toBeVisible();

    // 성공 메시지 확인
    await expect(page.locator('text=성공적으로 업로드되었습니다')).toBeVisible({ timeout: 30000 });

    // 대시보드 이동 버튼 확인
    await expect(page.locator('text=대시보드에서 확인하기')).toBeVisible();
  });

  test('잘못된 파일 형식 선택 시 오류 표시', async ({ page }) => {
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./test-data/document.pdf');

    // 오류 메시지 확인
    await expect(page.locator('text=엑셀 파일만')).toBeVisible();
  });
});
```

---

## 7. TDD 프로세스 적용

### 7.1 개발 순서 (Red-Green-Refactor)

**Phase 1: 프론트엔드 파일 검증**
1. RED: `useFileValidation.test.js` 작성 (실패)
2. GREEN: `useFileValidation.js` 구현 (통과)
3. REFACTOR: 코드 정리 및 최적화

**Phase 2: 프론트엔드 파일 업로드 로직**
1. RED: `useFileUpload.test.js` 작성 (실패)
2. GREEN: `useFileUpload.js` 구현 (통과)
3. REFACTOR: 에러 처리 개선

**Phase 3: 프론트엔드 UI 컴포넌트**
1. RED: 각 컴포넌트별 테스트 작성
2. GREEN: 컴포넌트 구현
3. REFACTOR: 스타일 및 접근성 개선

**Phase 4: 백엔드 Serializer**
1. RED: `test_serializers.py` 작성
2. GREEN: `FileUploadSerializer` 구현
3. REFACTOR: 검증 로직 개선

**Phase 5: 백엔드 View**
1. RED: `test_views.py` 작성
2. GREEN: `DataUploadView` 구현
3. REFACTOR: 예외 처리 개선

**Phase 6: 통합 테스트**
1. RED: 통합 테스트 작성
2. GREEN: 필요한 수정 사항 반영
3. REFACTOR: 전체 플로우 최적화

---

## 8. 구현 체크리스트

### 8.1 프론트엔드

- [ ] FileUploadArea 컴포넌트 구현
- [ ] FileInfo 컴포넌트 구현
- [ ] UploadButton 컴포넌트 구현
- [ ] UploadProgressBar 컴포넌트 구현
- [ ] FeedbackMessage 컴포넌트 구현
- [ ] useFileValidation 훅 구현
- [ ] useFileUpload 훅 구현
- [ ] UploadPage 메인 페이지 구현
- [ ] 모든 컴포넌트 단위 테스트 작성 및 통과
- [ ] 페이지 통합 테스트 작성 및 통과
- [ ] 접근성 검증 (키보드 네비게이션, 스크린 리더)
- [ ] 반응형 디자인 적용 (모바일, 태블릿, 데스크톱)

### 8.2 백엔드

- [ ] DataUploadView 구현
- [ ] FileUploadSerializer 구현
- [ ] 커스텀 예외 클래스 구현
- [ ] URL 라우팅 설정
- [ ] ExcelImportService 파일 읽기 로직 강화
- [ ] ExcelImportService 데이터 검증 로직 강화
- [ ] admin_required 데코레이터 적용
- [ ] Serializer 테스트 작성 및 통과
- [ ] View 테스트 작성 및 통과
- [ ] 통합 테스트 작성 및 통과
- [ ] 트랜잭션 롤백 검증

### 8.3 공통

- [ ] API 문서 작성 (Swagger/OpenAPI)
- [ ] 에러 메시지 일관성 검증
- [ ] 로깅 설정 확인
- [ ] 성능 테스트 (대용량 파일 처리)
- [ ] 보안 검토 (권한, 파일 검증)

---

## 9. 예상 소요 시간

| 작업 항목 | 예상 시간 |
|-----------|-----------|
| 프론트엔드 컴포넌트 구현 | 8시간 |
| 프론트엔드 훅 구현 | 4시간 |
| 프론트엔드 테스트 작성 | 6시간 |
| 백엔드 View 및 Serializer 구현 | 4시간 |
| 백엔드 ExcelImportService 강화 | 3시간 |
| 백엔드 테스트 작성 | 5시간 |
| 통합 테스트 및 디버깅 | 4시간 |
| 문서화 및 코드 리뷰 | 2시간 |
| **총계** | **36시간 (약 4.5일)** |

---

## 10. 리스크 및 완화 전략

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| 대용량 파일 처리 시 타임아웃 | 중 | 서버 타임아웃 설정 증가, 청크 단위 처리 고려 |
| 엑셀 파일 형식 다양성 | 중 | 철저한 검증 로직, 사용자 가이드 제공 |
| 데이터 검증 누락 | 높 | 모든 필수 컬럼 및 제약조건 검증, 단위 테스트 강화 |
| 트랜잭션 롤백 미작동 | 높 | @transaction.atomic 데코레이터 사용, 통합 테스트로 검증 |
| 업로드 중 사용자 이탈 | 낮 | 진행률 표시, 명확한 피드백 |

---

## 11. 참고 문서

- `/docs/PRD.md` - 제품 요구사항 정의서
- `/docs/userflow.md` - 사용자 플로우
- `/docs/usecases/02-excel-upload/spec.md` - 엑셀 업로드 유스케이스
- `/docs/database.md` - 데이터베이스 스키마
- `/docs/common-modules.md` - 공통 모듈
- `/docs/architecture.md` - 아키텍처 설계
- `/docs/rules/tdd.md` - TDD 가이드라인
- `/docs/input_data/*.csv` - 입력 데이터 샘플

---

**작성 완료일:** 2025-11-13
**최종 검토자:** Development Team
**승인일:** [TBD]
