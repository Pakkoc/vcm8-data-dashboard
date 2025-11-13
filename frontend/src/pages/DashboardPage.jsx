import { useEffect } from 'react';
import MainLayout from '../components/layout/MainLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import useApi from '../hooks/useApi';
import { dashboardAPI } from '../api/dashboardAPI';

// 차트 컴포넌트 import
import PerformanceBarChart from '../components/charts/PerformanceBarChart';
import PublicationLineChart from '../components/charts/PublicationLineChart';
import StudentPieChart from '../components/charts/StudentPieChart';
import BudgetGauge from '../components/charts/BudgetGauge';

const DashboardPage = () => {
  const { data, loading, error, execute } = useApi(dashboardAPI.getSummary);

  useEffect(() => {
    execute();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-[400px]">
          <LoadingSpinner size="large" />
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <ErrorMessage message={error} onRetry={execute} />
      </MainLayout>
    );
  }

  if (data?.is_empty) {
    return (
      <MainLayout>
        <EmptyState
          message="표시할 데이터가 없습니다. 관리자가 데이터를 업로드해야 합니다."
          icon="📊"
        />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">메인 대시보드</h1>
        <p className="text-gray-600 mt-2">대학교 핵심 성과 지표를 한눈에 확인하세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 학과별 성과 - 막대 그래프 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            학과별 종합 실적
          </h2>
          <PerformanceBarChart data={data?.performance_by_department} />
        </div>

        {/* 연도별 논문 수 - 라인 차트 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            논문 게재 수 추이
          </h2>
          <PublicationLineChart data={data?.publications_by_year} />
        </div>

        {/* 학생 현황 - 파이 차트 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            재학생 학적 상태
          </h2>
          <StudentPieChart data={data?.students_by_status} />
        </div>

        {/* 예산 집행률 - 게이지 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">
            연구비 예산 집행률
          </h2>
          <BudgetGauge data={data?.budget_execution} />
        </div>
      </div>
    </MainLayout>
  );
};

export default DashboardPage;
