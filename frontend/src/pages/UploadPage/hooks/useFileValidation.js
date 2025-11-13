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
