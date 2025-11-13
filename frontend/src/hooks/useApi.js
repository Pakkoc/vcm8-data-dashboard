import { useState } from 'react';

/**
 * API 호출을 위한 커스텀 훅
 * @param {Function} apiFunc - API 호출 함수
 */
const useApi = (apiFunc) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (...params) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiFunc(...params);
      setData(result);
      return result;
    } catch (err) {
      const errorMessage =
        err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
    setLoading(false);
  };

  return { data, loading, error, execute, reset };
};

export default useApi;
