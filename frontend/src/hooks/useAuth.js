import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { authAPI } from '../api/authAPI';

const useAuth = () => {
  const { user, isAuthenticated, setUser, logout: storeLogout } = useAuthStore();
  const navigate = useNavigate();

  const login = async (email, password) => {
    try {
      // 1. Supabase Auth 로그인 API 호출
      const { access_token, user: userData } = await authAPI.login(
        email,
        password
      );

      // 2. 토큰을 localStorage에 저장
      localStorage.setItem('access_token', access_token);

      // 3. 사용자 프로필 조회 (role 정보 포함)
      const profile = await authAPI.getProfile();

      // 4. 전역 상태에 사용자 정보 저장
      setUser({
        ...userData,
        role: profile.role,
        username: profile.username
      });

      // 5. 대시보드로 리디렉션
      navigate('/dashboard');
    } catch (error) {
      console.error('로그인 실패:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      storeLogout();
      navigate('/login');
    }
  };

  return { user, isAuthenticated, login, logout };
};

export default useAuth;
