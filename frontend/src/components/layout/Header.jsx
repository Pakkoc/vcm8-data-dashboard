import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import { authAPI } from '../../api/authAPI';

const Header = () => {
  const { user, isAdmin, logout } = useAuthStore();
  const navigate = useNavigate();
  const [isDataMenuOpen, setIsDataMenuOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      logout();
      navigate('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
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

          <div
            className="relative"
            onMouseEnter={() => setIsDataMenuOpen(true)}
            onMouseLeave={() => setIsDataMenuOpen(false)}
          >
            <button className="hover:text-blue-600 transition-colors">
              데이터 관리 ▼
            </button>
            {isDataMenuOpen && (
              <div className="absolute top-full left-0 mt-1 bg-white shadow-lg rounded-md py-2 min-w-[180px] z-50">
                <Link
                  to="/colleges"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  단과대학
                </Link>
                <Link
                  to="/departments"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  학과
                </Link>
                <Link
                  to="/students"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  학생
                </Link>
                <Link
                  to="/kpis"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  학과 KPI
                </Link>
                <Link
                  to="/publications"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  논문
                </Link>
                <Link
                  to="/projects"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  연구과제
                </Link>
                <Link
                  to="/expenses"
                  className="block px-4 py-2 hover:bg-gray-100"
                >
                  과제집행내역
                </Link>
              </div>
            )}
          </div>

          {isAdmin() && (
            <Link
              to="/upload"
              className="hover:text-blue-600 transition-colors"
            >
              파일 업로드
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
