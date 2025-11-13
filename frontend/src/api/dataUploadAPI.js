import apiClient from './index';

export const dataUploadAPI = {
  /**
   * 엑셀 파일 업로드
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
};
