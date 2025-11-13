import apiClient from './index';

export const dashboardAPI = {
  /**
   * 대시보드 요약 데이터 조회
   */
  getSummary: async () => {
    const response = await apiClient.get('/dashboard/summary/');
    return response.data;
  },
};
