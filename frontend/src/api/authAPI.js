import apiClient from './index';

export const authAPI = {
  /**
   * 로그인
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access_token: string, user: object}>}
   */
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login/', { email, password });
    return response.data;
  },

  /**
   * 로그아웃
   */
  logout: async () => {
    await apiClient.post('/auth/logout/');
    localStorage.removeItem('access_token');
  },

  /**
   * 사용자 프로필 조회
   */
  getProfile: async () => {
    const response = await apiClient.get('/auth/profile/');
    return response.data;
  },
};
