import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import { authAPI } from '../../api/authAPI';

const Header = () => {
  const { user, isAdmin, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      logout();
      navigate('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
      // 에러가 발생해도 로컬 로그아웃은 처리
      logout();
      navigate('/login');
    }
  };

  return (
    <header className="bg-white shadow">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/dashboard" className="text-xl font-bold text-blue-600">
          대학 데이터 대시보드
        </Link>

        <div className="flex items-center gap-4">
          <Link
            to="/dashboard"
            className="hover:text-blue-600 transition-colors"
          >
            대시보드
          </Link>

          {isAdmin() && (
            <Link
              to="/upload"
              className="hover:text-blue-600 transition-colors"
            >
              데이터 관리
            </Link>
          )}

          <div className="flex items-center gap-2 border-l pl-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:underline"
            >
              로그아웃
            </button>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
