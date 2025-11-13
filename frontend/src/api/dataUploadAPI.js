import apiClient from './index';

export const dataUploadAPI = {
  /**
   * 단일 엑셀 파일 업로드
   * @param {File} file
   */
  uploadExcel: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/data-upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * 여러 파일 동시 업로드
   * @param {File[]} files
   */
  uploadMultipleFiles: async (files) => {
    const formData = new FormData();

    // 'files' 필드로 여러 파일 추가
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await apiClient.post('/data-upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
