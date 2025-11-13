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
              errorMessage += '\\n' + data.details.join('\\n');
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
