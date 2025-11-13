import apiClient from './index';

// ============= Generic CRUD Functions =============

const createCRUDAPI = (resourcePath) => ({
  // 목록 조회
  getAll: async () => {
    const response = await apiClient.get(`/dashboard/${resourcePath}/`);
    return response.data;
  },

  // 단건 조회
  getOne: async (id) => {
    const response = await apiClient.get(`/dashboard/${resourcePath}/${id}/`);
    return response.data;
  },

  // 생성
  create: async (data) => {
    const response = await apiClient.post(`/dashboard/${resourcePath}/`, data);
    return response.data;
  },

  // 수정
  update: async (id, data) => {
    const response = await apiClient.put(
      `/dashboard/${resourcePath}/${id}/`,
      data
    );
    return response.data;
  },

  // 부분 수정
  patch: async (id, data) => {
    const response = await apiClient.patch(
      `/dashboard/${resourcePath}/${id}/`,
      data
    );
    return response.data;
  },

  // 삭제
  delete: async (id) => {
    const response = await apiClient.delete(
      `/dashboard/${resourcePath}/${id}/`
    );
    return response.data;
  },
});

// ============= Resource-specific APIs =============

export const collegeAPI = createCRUDAPI('colleges');
export const departmentAPI = createCRUDAPI('departments');
export const studentAPI = createCRUDAPI('students');
export const kpiAPI = createCRUDAPI('kpis');
export const publicationAPI = createCRUDAPI('publications');
export const researchProjectAPI = createCRUDAPI('projects');
export const projectExpenseAPI = createCRUDAPI('expenses');
