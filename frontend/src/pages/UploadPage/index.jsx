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
