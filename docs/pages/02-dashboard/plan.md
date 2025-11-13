# 메인 대시보드 페이지 구현 계획

**작성일:** 2025-11-13
**페이지 ID:** 02-dashboard
**우선순위:** P0 (최우선)
**관련 유스케이스:** UC-003 (메인 대시보드 조회)

---

## 1. 개요

### 1.1 목적
사용자가 대학교의 핵심 성과 지표를 직관적인 차트 형태로 확인할 수 있는 메인 대시보드 페이지를 구현합니다. 백엔드에서 집계된 데이터를 Recharts 라이브러리를 사용하여 4가지 차트 타입으로 시각화합니다.

### 1.2 범위
- 프론트엔드: 4가지 차트 컴포넌트 개발 (막대, 라인, 파이, 게이지)
- 백엔드: 대시보드 API 엔드포인트 및 데이터 집계 로직 (이미 구현 완료)
- 테스트: 단위 테스트 및 통합 테스트

### 1.3 제외 항목 (MVP 범위 외)
- 차트 데이터 필터링 및 정렬 기능
- 차트 데이터 드릴다운 기능
- 데이터 다운로드 기능
- 차트 인터랙션 커스터마이징 (Recharts 기본 기능만 사용)

---

## 2. 참조 문서

### 2.1 핵심 문서
- `/docs/PRD.md` - 제품 요구사항 (섹션 3.3 메인 대시보드 페이지)
- `/docs/userflow.md` - 사용자 플로우 (섹션 3.1)
- `/docs/usecases/03-main-dashboard-view/spec.md` - 대시보드 조회 유스케이스
- `/docs/architecture.md` - 아키텍처 설계
- `/docs/database.md` - 데이터베이스 스키마
- `/docs/common-modules.md` - 공통 모듈 (이미 구현 완료)

### 2.2 데이터 참조
- `/docs/input_data/student_roster.csv` - 학생 데이터 형식
- `/docs/input_data/publication_list.csv` - 논문 데이터 형식
- `/docs/input_data/research_project_data.csv` - 연구 과제 데이터 형식
- `/docs/input_data/department_kpi.csv` - 학과 KPI 데이터 형식

---

## 3. 현재 구현 상태 분석

### 3.1 백엔드 (이미 구현 완료)

#### 구현된 컴포넌트
1. **Repository Layer**: `backend/apps/dashboard/repositories.py`
   - `StudentRepository`: 학생 데이터 접근
   - `PublicationRepository`: 논문 데이터 접근 및 연도별 집계
   - `ProjectExpenseRepository`: 예산 집행 데이터 접근
   - `ResearchProjectRepository`: 연구 과제 데이터 접근
   - `DepartmentRepository`: 학과 데이터 접근

2. **Service Layer**: `backend/apps/dashboard/services/summary_generator.py`
   - `DashboardSummaryService`: 대시보드 데이터 집계 로직
   - 메소드:
     - `generate_dashboard_summary()`: 전체 대시보드 데이터 생성
     - `_get_performance_by_department()`: 학과별 성과 집계
     - `_get_publications_by_year()`: 연도별 논문 수 집계
     - `_get_students_by_status()`: 학적 상태별 학생 수 집계
     - `_get_budget_execution()`: 예산 집행률 계산

3. **API Endpoint**: (구현 필요 - View Layer)
   - 엔드포인트: `GET /api/v1/dashboard/summary/`
   - 응답 형식:
     ```json
     {
       "is_empty": false,
       "performance_by_department": [
         {
           "department_name": "컴퓨터공학과",
           "college_name": "공과대학",
           "student_count": 120,
           "publication_count": 15,
           "project_count": 8,
           "total_funding": 500000000
         }
       ],
       "publications_by_year": [
         { "year": 2023, "count": 50 },
         { "year": 2024, "count": 65 }
       ],
       "students_by_status": [
         { "status": "재학", "count": 450 },
         { "status": "휴학", "count": 30 }
       ],
       "budget_execution": {
         "total_budget": 1600000000,
         "executed_amount": 1283500000,
         "pending_amount": 165000000,
         "execution_rate": 80.22
       }
     }
     ```

### 3.2 프론트엔드 (부분 구현)

#### 구현된 컴포넌트
1. **페이지 구조**: `frontend/src/pages/DashboardPage.jsx`
   - 기본 레이아웃 완료
   - API 호출 로직 완료 (useApi 훅 사용)
   - 로딩/에러/빈 데이터 상태 처리 완료
   - 4개 차트 영역 placeholder 존재

2. **공통 모듈** (이미 구현 완료)
   - `useApi`: API 호출 커스텀 훅
   - `dashboardAPI`: API 클라이언트
   - `LoadingSpinner`, `ErrorMessage`, `EmptyState`: 상태 컴포넌트
   - `MainLayout`: 페이지 레이아웃

#### 미구현 컴포넌트
- 4가지 차트 컴포넌트 (막대, 라인, 파이, 게이지)

---

## 4. 구현 계획

### 4.1 Phase 1: 백엔드 View Layer 구현 (TDD)

#### 4.1.1 테스트 작성
**파일 경로:** `backend/apps/dashboard/tests/test_views.py`

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestDashboardSummaryView:
    """대시보드 요약 API 테스트"""

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('dashboard-summary')

    def test_dashboard_summary_requires_authentication(self):
        """인증 없이 접근 시 401 응답"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_summary_with_empty_data(self, authenticated_user):
        """데이터가 없을 때 is_empty=True 반환"""
        self.client.force_authenticate(user=authenticated_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_empty'] is True

    def test_dashboard_summary_with_data(
        self, authenticated_user, sample_departments, sample_students, sample_publications
    ):
        """데이터가 있을 때 정상 응답"""
        self.client.force_authenticate(user=authenticated_user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_empty'] is False
        assert 'performance_by_department' in response.data
        assert 'publications_by_year' in response.data
        assert 'students_by_status' in response.data
        assert 'budget_execution' in response.data

    def test_dashboard_summary_performance_data_structure(
        self, authenticated_user, sample_data
    ):
        """학과별 성과 데이터 구조 검증"""
        self.client.force_authenticate(user=authenticated_user)
        response = self.client.get(self.url)

        performance = response.data['performance_by_department']
        assert len(performance) > 0
        assert 'department_name' in performance[0]
        assert 'student_count' in performance[0]
        assert 'publication_count' in performance[0]

    def test_dashboard_summary_response_time(self, authenticated_user, large_dataset):
        """대용량 데이터에서 응답 시간 2초 이내"""
        import time

        self.client.force_authenticate(user=authenticated_user)
        start = time.time()
        response = self.client.get(self.url)
        duration = time.time() - start

        assert response.status_code == status.HTTP_200_OK
        assert duration < 2.0
```

#### 4.1.2 View 구현
**파일 경로:** `backend/apps/dashboard/views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services.summary_generator import DashboardSummaryService
from .serializers import DashboardSummarySerializer


class DashboardSummaryView(APIView):
    """대시보드 요약 데이터 조회 API"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        대시보드 요약 데이터 반환

        Returns:
            HTTP 200 OK: 대시보드 데이터
            HTTP 401 Unauthorized: 인증 실패
            HTTP 500 Internal Server Error: 서버 오류
        """
        try:
            service = DashboardSummaryService()
            summary_data = service.generate_dashboard_summary()

            serializer = DashboardSummarySerializer(data=summary_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            # 로그 기록
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Dashboard summary generation failed: {str(e)}")

            return Response(
                {'error': '데이터를 불러오는 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

#### 4.1.3 URL 라우팅
**파일 경로:** `backend/apps/dashboard/urls.py`

```python
from django.urls import path
from .views import DashboardSummaryView

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]
```

**프로젝트 URL 통합:** `backend/dashboard_project/urls.py`
```python
urlpatterns = [
    # ...
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
]
```

#### 4.1.4 예상 소요 시간
- 테스트 작성: 2시간
- View 구현: 1시간
- URL 라우팅: 0.5시간
- 테스트 실행 및 디버깅: 1시간
- **합계: 4.5시간**

---

### 4.2 Phase 2: 프론트엔드 차트 컴포넌트 구현 (TDD)

#### 4.2.1 공통 차트 유틸리티
**파일 경로:** `frontend/src/utils/chartHelpers.js`

```javascript
/**
 * 숫자를 천 단위 콤마 형식으로 변환
 * @param {number} value
 * @returns {string}
 */
export const formatNumber = (value) => {
  return new Intl.NumberFormat('ko-KR').format(value);
};

/**
 * 금액을 억원 단위로 변환
 * @param {number} value - 원 단위 금액
 * @returns {string}
 */
export const formatCurrency = (value) => {
  const billions = value / 100000000;
  return `${billions.toFixed(1)}억원`;
};

/**
 * 차트 색상 팔레트
 */
export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
  neutral: '#6b7280'
};

/**
 * 파이 차트용 색상 배열
 */
export const PIE_COLORS = [
  '#3b82f6',
  '#8b5cf6',
  '#10b981',
  '#f59e0b',
  '#ef4444'
];
```

#### 4.2.2 차트 컴포넌트 1: 학과별 성과 (막대 그래프)

**테스트 파일:** `frontend/src/components/charts/__tests__/PerformanceBarChart.test.jsx`

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PerformanceBarChart from '../PerformanceBarChart';

describe('PerformanceBarChart', () => {
  const mockData = [
    {
      department_name: '컴퓨터공학과',
      student_count: 120,
      publication_count: 15,
      project_count: 8
    },
    {
      department_name: '전자공학과',
      student_count: 100,
      publication_count: 12,
      project_count: 6
    }
  ];

  it('renders chart with data', () => {
    render(<PerformanceBarChart data={mockData} />);
    expect(screen.getByText('컴퓨터공학과')).toBeInTheDocument();
  });

  it('renders empty state when data is empty', () => {
    render(<PerformanceBarChart data={[]} />);
    expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
  });

  it('displays correct metric labels', () => {
    render(<PerformanceBarChart data={mockData} />);
    expect(screen.getByText(/학생 수/i)).toBeInTheDocument();
    expect(screen.getByText(/논문 수/i)).toBeInTheDocument();
  });
});
```

**컴포넌트 파일:** `frontend/src/components/charts/PerformanceBarChart.jsx`

```javascript
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import EmptyState from '../common/EmptyState';
import { CHART_COLORS, formatNumber } from '../../utils/chartHelpers';

const PerformanceBarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <EmptyState message="학과별 성과 데이터가 없습니다." />;
  }

  // 차트 표시용 데이터 변환
  const chartData = data.map(item => ({
    name: item.department_name,
    학생수: item.student_count,
    논문수: item.publication_count,
    과제수: item.project_count
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        <p className="font-semibold text-sm mb-2">{payload[0].payload.name}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-xs" style={{ color: entry.color }}>
            {entry.name}: {formatNumber(entry.value)}
          </p>
        ))}
      </div>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={chartData}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 12 }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Bar dataKey="학생수" fill={CHART_COLORS.primary} />
        <Bar dataKey="논문수" fill={CHART_COLORS.secondary} />
        <Bar dataKey="과제수" fill={CHART_COLORS.success} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default PerformanceBarChart;
```

#### 4.2.3 차트 컴포넌트 2: 연도별 논문 수 추이 (라인 차트)

**테스트 파일:** `frontend/src/components/charts/__tests__/PublicationLineChart.test.jsx`

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PublicationLineChart from '../PublicationLineChart';

describe('PublicationLineChart', () => {
  const mockData = [
    { year: 2023, count: 50 },
    { year: 2024, count: 65 },
    { year: 2025, count: 72 }
  ];

  it('renders line chart with data', () => {
    render(<PublicationLineChart data={mockData} />);
    expect(screen.getByText('2023')).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    render(<PublicationLineChart data={[]} />);
    expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
  });
});
```

**컴포넌트 파일:** `frontend/src/components/charts/PublicationLineChart.jsx`

```javascript
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import EmptyState from '../common/EmptyState';
import { CHART_COLORS, formatNumber } from '../../utils/chartHelpers';

const PublicationLineChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <EmptyState message="연도별 논문 데이터가 없습니다." />;
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        <p className="font-semibold text-sm mb-1">{payload[0].payload.year}년</p>
        <p className="text-xs text-gray-600">
          논문 수: {formatNumber(payload[0].value)}
        </p>
      </div>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="year"
          tick={{ fontSize: 12 }}
          label={{ value: '연도', position: 'insideBottom', offset: -5 }}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          label={{ value: '논문 수', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
        <Line
          type="monotone"
          dataKey="count"
          stroke={CHART_COLORS.primary}
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
          name="논문 수"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PublicationLineChart;
```

#### 4.2.4 차트 컴포넌트 3: 학생 현황 (파이 차트)

**테스트 파일:** `frontend/src/components/charts/__tests__/StudentPieChart.test.jsx`

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StudentPieChart from '../StudentPieChart';

describe('StudentPieChart', () => {
  const mockData = [
    { status: '재학', count: 450 },
    { status: '휴학', count: 30 },
    { status: '졸업', count: 200 }
  ];

  it('renders pie chart with data', () => {
    render(<StudentPieChart data={mockData} />);
    expect(screen.getByText('재학')).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    render(<StudentPieChart data={[]} />);
    expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
  });
});
```

**컴포넌트 파일:** `frontend/src/components/charts/StudentPieChart.jsx`

```javascript
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import EmptyState from '../common/EmptyState';
import { PIE_COLORS, formatNumber } from '../../utils/chartHelpers';

const StudentPieChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <EmptyState message="학생 현황 데이터가 없습니다." />;
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0];
    const total = payload[0].payload.total;
    const percentage = ((data.value / total) * 100).toFixed(1);

    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        <p className="font-semibold text-sm mb-1">{data.name}</p>
        <p className="text-xs text-gray-600">
          인원: {formatNumber(data.value)}명 ({percentage}%)
        </p>
      </div>
    );
  };

  // 전체 학생 수 계산
  const total = data.reduce((sum, item) => sum + item.count, 0);

  // 차트 데이터에 total 추가
  const chartData = data.map(item => ({
    name: item.status,
    value: item.count,
    total: total
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default StudentPieChart;
```

#### 4.2.5 차트 컴포넌트 4: 예산 집행률 (게이지 차트)

**테스트 파일:** `frontend/src/components/charts/__tests__/BudgetGauge.test.jsx`

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import BudgetGauge from '../BudgetGauge';

describe('BudgetGauge', () => {
  const mockData = {
    total_budget: 1600000000,
    executed_amount: 1283500000,
    pending_amount: 165000000,
    execution_rate: 80.22
  };

  it('displays execution rate', () => {
    render(<BudgetGauge data={mockData} />);
    expect(screen.getByText(/80.22%/)).toBeInTheDocument();
  });

  it('shows budget amounts', () => {
    render(<BudgetGauge data={mockData} />);
    expect(screen.getByText(/총 예산/)).toBeInTheDocument();
    expect(screen.getByText(/집행 완료/)).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    render(<BudgetGauge data={null} />);
    expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
  });
});
```

**컴포넌트 파일:** `frontend/src/components/charts/BudgetGauge.jsx`

```javascript
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Label
} from 'recharts';
import EmptyState from '../common/EmptyState';
import { formatCurrency, CHART_COLORS } from '../../utils/chartHelpers';

const BudgetGauge = ({ data }) => {
  if (!data) {
    return <EmptyState message="예산 집행 데이터가 없습니다." />;
  }

  const { total_budget, executed_amount, pending_amount, execution_rate } = data;

  // 게이지 차트 데이터 (0-100 범위를 180도로 표현)
  const gaugeData = [
    { value: execution_rate, fill: CHART_COLORS.success },
    { value: 100 - execution_rate, fill: '#e5e7eb' }
  ];

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={gaugeData}
            cx="50%"
            cy="80%"
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={90}
            dataKey="value"
          >
            {gaugeData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
            <Label
              value={`${execution_rate}%`}
              position="center"
              style={{ fontSize: '24px', fontWeight: 'bold', fill: CHART_COLORS.success }}
            />
          </Pie>
        </PieChart>
      </ResponsiveContainer>

      {/* 상세 정보 */}
      <div className="mt-4 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">총 예산:</span>
          <span className="font-semibold">{formatCurrency(total_budget)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">집행 완료:</span>
          <span className="font-semibold text-green-600">
            {formatCurrency(executed_amount)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">처리 중:</span>
          <span className="font-semibold text-yellow-600">
            {formatCurrency(pending_amount)}
          </span>
        </div>
        <div className="flex justify-between pt-2 border-t">
          <span className="text-gray-600">집행률:</span>
          <span className="font-bold text-green-600 text-lg">
            {execution_rate}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default BudgetGauge;
```

#### 4.2.6 DashboardPage 업데이트

**파일 경로:** `frontend/src/pages/DashboardPage.jsx`

```javascript
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
```

#### 4.2.7 예상 소요 시간
- 공통 유틸리티: 1시간
- 차트 컴포넌트 1 (막대): 2시간 (테스트 포함)
- 차트 컴포넌트 2 (라인): 1.5시간
- 차트 컴포넌트 3 (파이): 1.5시간
- 차트 컴포넌트 4 (게이지): 2시간
- DashboardPage 통합: 1시간
- **합계: 9시간**

---

### 4.3 Phase 3: 통합 테스트 및 E2E 테스트

#### 4.3.1 백엔드 통합 테스트
**파일 경로:** `backend/apps/dashboard/tests/test_integration.py`

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestDashboardIntegration:
    """대시보드 전체 플로우 통합 테스트"""

    def test_complete_dashboard_flow(
        self, authenticated_user, complete_dataset
    ):
        """데이터 업로드 후 대시보드 조회 시나리오"""
        client = APIClient()
        client.force_authenticate(user=authenticated_user)

        # 1. 대시보드 조회
        url = reverse('dashboard-summary')
        response = client.get(url)

        # 2. 응답 검증
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_empty'] is False

        # 3. 각 차트 데이터 존재 확인
        assert len(response.data['performance_by_department']) > 0
        assert len(response.data['publications_by_year']) > 0
        assert len(response.data['students_by_status']) > 0
        assert response.data['budget_execution']['execution_rate'] > 0

    def test_dashboard_with_partial_data(
        self, authenticated_user, partial_dataset
    ):
        """일부 데이터만 있는 경우"""
        client = APIClient()
        client.force_authenticate(user=authenticated_user)

        url = reverse('dashboard-summary')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # 일부 차트는 빈 배열일 수 있음
        assert 'performance_by_department' in response.data

    def test_concurrent_dashboard_requests(
        self, authenticated_user, complete_dataset
    ):
        """동시 요청 처리"""
        import concurrent.futures

        client = APIClient()
        client.force_authenticate(user=authenticated_user)
        url = reverse('dashboard-summary')

        def make_request():
            return client.get(url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]

        # 모든 요청이 성공해야 함
        assert all(r.status_code == status.HTTP_200_OK for r in results)
```

#### 4.3.2 프론트엔드 통합 테스트
**파일 경로:** `frontend/src/pages/__tests__/DashboardPage.integration.test.jsx`

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DashboardPage from '../DashboardPage';
import { dashboardAPI } from '../../api/dashboardAPI';

vi.mock('../../api/dashboardAPI');

describe('DashboardPage Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays all charts when data is available', async () => {
    const mockData = {
      is_empty: false,
      performance_by_department: [
        { department_name: '컴퓨터공학과', student_count: 120, publication_count: 15 }
      ],
      publications_by_year: [
        { year: 2023, count: 50 }
      ],
      students_by_status: [
        { status: '재학', count: 450 }
      ],
      budget_execution: {
        total_budget: 1600000000,
        executed_amount: 1283500000,
        execution_rate: 80.22
      }
    };

    dashboardAPI.getSummary.mockResolvedValue(mockData);

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // 로딩 확인
    expect(screen.getByRole('status')).toBeInTheDocument();

    // 데이터 로드 후 차트 표시 확인
    await waitFor(() => {
      expect(screen.getByText('학과별 종합 실적')).toBeInTheDocument();
      expect(screen.getByText('논문 게재 수 추이')).toBeInTheDocument();
      expect(screen.getByText('재학생 학적 상태')).toBeInTheDocument();
      expect(screen.getByText('연구비 예산 집행률')).toBeInTheDocument();
    });
  });

  it('displays empty state when no data', async () => {
    dashboardAPI.getSummary.mockResolvedValue({ is_empty: true });

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/데이터가 없습니다/i)).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    dashboardAPI.getSummary.mockRejectedValue(new Error('Network error'));

    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/불러오는 데 실패했습니다/i)).toBeInTheDocument();
    });
  });
});
```

#### 4.3.3 예상 소요 시간
- 백엔드 통합 테스트: 2시간
- 프론트엔드 통합 테스트: 2시간
- E2E 테스트 (Playwright - 선택): 3시간
- **합계: 4-7시간**

---

## 5. 에러 핸들링 및 엣지 케이스

### 5.1 백엔드 에러 처리

#### 5.1.1 데이터가 없는 경우
- **상황**: 데이터베이스에 아무 데이터도 없음
- **처리**: `is_empty: true` 반환 (HTTP 200 OK)
- **프론트엔드**: EmptyState 컴포넌트 표시

#### 5.1.2 부분 데이터만 있는 경우
- **상황**: 일부 테이블은 비어있음 (예: 논문 데이터 없음)
- **처리**: 해당 차트는 빈 배열 반환, 다른 차트는 정상 표시
- **프론트엔드**: 개별 차트에서 EmptyState 표시

#### 5.1.3 데이터베이스 연결 실패
- **상황**: PostgreSQL 연결 오류
- **처리**: HTTP 500 응답 + 에러 로그 기록
- **프론트엔드**: ErrorMessage 컴포넌트 + 재시도 버튼

#### 5.1.4 쿼리 성능 문제
- **상황**: 대용량 데이터로 인한 느린 응답
- **처리**: 데이터베이스 인덱스 최적화, 쿼리 최적화
- **목표**: 2초 이내 응답

### 5.2 프론트엔드 에러 처리

#### 5.2.1 API 호출 실패
- **상황**: 네트워크 오류, 서버 다운
- **처리**: ErrorMessage 표시 + 재시도 버튼

#### 5.2.2 인증 토큰 만료
- **상황**: HTTP 401 응답
- **처리**: Axios Interceptor에서 자동 로그인 페이지 리다이렉트

#### 5.2.3 데이터 형식 오류
- **상황**: API 응답 데이터 구조가 예상과 다름
- **처리**: try-catch로 감싸고 fallback 표시

#### 5.2.4 차트 렌더링 오류
- **상황**: Recharts 라이브러리 오류
- **처리**: ErrorBoundary 컴포넌트로 감싸기

---

## 6. 성능 최적화

### 6.1 백엔드 최적화

#### 6.1.1 데이터베이스 쿼리 최적화
```python
# Repository에서 select_related 사용
class DepartmentRepository:
    def get_all(self):
        return list(
            self.model_class.objects
            .select_related('college')  # N+1 쿼리 방지
            .all()
        )
```

#### 6.1.2 집계 쿼리 최적화
- COUNT, SUM 등 집계 함수는 데이터베이스 수준에서 처리
- 인덱스 활용 (이미 database.md에 정의됨)

#### 6.1.3 캐싱 (선택 사항 - MVP 이후)
```python
from django.core.cache import cache

def generate_dashboard_summary(self):
    cache_key = 'dashboard_summary'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    data = self._generate_summary()
    cache.set(cache_key, data, timeout=300)  # 5분 캐싱
    return data
```

### 6.2 프론트엔드 최적화

#### 6.2.1 컴포넌트 메모이제이션
```javascript
import { memo } from 'react';

const PerformanceBarChart = memo(({ data }) => {
  // ...
});
```

#### 6.2.2 Lazy Loading (선택)
```javascript
import { lazy, Suspense } from 'react';

const PerformanceBarChart = lazy(() => import('./PerformanceBarChart'));

// 사용
<Suspense fallback={<LoadingSpinner />}>
  <PerformanceBarChart data={data} />
</Suspense>
```

#### 6.2.3 차트 렌더링 최적화
- Recharts의 `isAnimationActive={false}` 옵션 (대용량 데이터 시)
- ResponsiveContainer의 debounce 설정

---

## 7. 테스트 전략

### 7.1 TDD 프로세스 준수

#### Red-Green-Refactor 사이클
1. **Red**: 테스트 작성 (실패 확인)
2. **Green**: 최소 구현으로 통과
3. **Refactor**: 코드 정리 (테스트 통과 유지)

#### 테스트 우선순위
1. **단위 테스트 (70%)**
   - Repository 메소드
   - Service 로직
   - 차트 컴포넌트

2. **통합 테스트 (20%)**
   - API 엔드포인트
   - 페이지 전체 플로우

3. **E2E 테스트 (10%)**
   - 로그인 → 대시보드 조회 시나리오

### 7.2 테스트 커버리지 목표
- 백엔드: 80% 이상
- 프론트엔드: 70% 이상

### 7.3 테스트 실행 명령어
```bash
# 백엔드
pytest apps/dashboard/tests/ --cov=apps/dashboard --cov-report=html

# 프론트엔드
npm run test -- --coverage
```

---

## 8. 의존성 라이브러리

### 8.1 프론트엔드
```json
{
  "dependencies": {
    "recharts": "^2.10.0",
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0"
  }
}
```

### 8.2 백엔드
```
Django==5.0
djangorestframework==3.14.0
psycopg2-binary==2.9.9
pytest==7.4.0
pytest-django==4.7.0
pytest-cov==4.1.0
```

---

## 9. 구현 순서 및 일정

### 9.1 Day 1 (8시간)
- [x] 백엔드 공통 모듈 확인 (이미 완료)
- [ ] 백엔드 View Layer 테스트 작성 (2h)
- [ ] 백엔드 View 구현 및 URL 라우팅 (1.5h)
- [ ] 백엔드 테스트 실행 및 디버깅 (1h)
- [ ] 프론트엔드 공통 유틸리티 작성 (1h)
- [ ] 차트 컴포넌트 1 (막대) 구현 (2.5h)

### 9.2 Day 2 (8시간)
- [ ] 차트 컴포넌트 2 (라인) 구현 (1.5h)
- [ ] 차트 컴포넌트 3 (파이) 구현 (1.5h)
- [ ] 차트 컴포넌트 4 (게이지) 구현 (2h)
- [ ] DashboardPage 통합 (1h)
- [ ] 프론트엔드 단위 테스트 실행 (1h)
- [ ] 스타일링 및 반응형 조정 (1h)

### 9.3 Day 3 (4-7시간)
- [ ] 백엔드 통합 테스트 (2h)
- [ ] 프론트엔드 통합 테스트 (2h)
- [ ] E2E 테스트 (선택, 3h)
- [ ] 버그 수정 및 리팩토링 (1-2h)

**총 예상 소요 시간: 20-23시간 (약 3일)**

---

## 10. 검증 체크리스트

### 10.1 기능 검증
- [ ] 로그인 후 대시보드 페이지 자동 로드
- [ ] 4개 차트 모두 정상 표시
- [ ] 데이터가 없을 때 적절한 안내 메시지 표시
- [ ] API 오류 시 재시도 버튼 작동
- [ ] 차트 호버 시 툴팁 표시
- [ ] 반응형 레이아웃 (모바일/태블릿/데스크톱)

### 10.2 성능 검증
- [ ] API 응답 시간 2초 이내
- [ ] 차트 렌더링 1초 이내
- [ ] 동시 접속 50명 지원

### 10.3 테스트 검증
- [ ] 백엔드 단위 테스트 모두 통과
- [ ] 프론트엔드 단위 테스트 모두 통과
- [ ] 통합 테스트 모두 통과
- [ ] 테스트 커버리지 목표 달성 (백엔드 80%, 프론트엔드 70%)

### 10.4 코드 품질
- [ ] ESLint 경고 없음
- [ ] Prettier 포맷팅 적용
- [ ] 주석 및 문서화 완료
- [ ] DRY 원칙 준수

---

## 11. 리스크 관리

### 11.1 기술적 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| Recharts 학습 곡선 | 중 | 공식 문서 사전 학습, 예제 코드 참조 |
| 대용량 데이터 렌더링 성능 | 중 | 데이터 제한 (상위 10개), 페이지네이션 (미래) |
| 차트 호환성 문제 | 낮 | 최신 Recharts 안정 버전 사용 |
| API 응답 지연 | 중 | 데이터베이스 쿼리 최적화, 인덱스 활용 |

### 11.2 일정 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| 차트 구현 시간 초과 | 중 | 복잡한 커스터마이징 배제, 기본 기능만 |
| 테스트 작성 시간 부족 | 높 | TDD 프로세스 엄격히 준수, 핵심 시나리오 집중 |
| 통합 이슈 | 중 | 일일 통합 테스트, 조기 발견 |

---

## 12. 완료 기준 (Definition of Done)

1. [ ] 모든 코드가 TDD 프로세스를 따라 작성됨
2. [ ] 모든 테스트가 통과함 (단위 + 통합)
3. [ ] 테스트 커버리지 목표 달성
4. [ ] 로컬 환경에서 정상 동작 확인
5. [ ] 코드 리뷰 완료 (팀원 1명 이상)
6. [ ] 문서화 완료 (README, API 문서)
7. [ ] Git commit 및 PR 생성
8. [ ] 배포 준비 완료 (환경 변수 설정 등)

---

## 13. 다음 단계

대시보드 페이지 구현 완료 후:
1. **데이터 업로드 페이지 구현** (UC-002)
2. **로그인 페이지 구현** (UC-001)
3. **전체 시스템 통합 테스트**
4. **Railway 배포**

---

## 부록

### A. API 응답 예시

```json
{
  "is_empty": false,
  "performance_by_department": [
    {
      "department_name": "컴퓨터공학과",
      "college_name": "공과대학",
      "student_count": 120,
      "publication_count": 15,
      "project_count": 8,
      "total_funding": 800000000
    },
    {
      "department_name": "전자공학과",
      "college_name": "공과대학",
      "student_count": 100,
      "publication_count": 12,
      "project_count": 6,
      "total_funding": 500000000
    }
  ],
  "publications_by_year": [
    { "year": 2023, "count": 50 },
    { "year": 2024, "count": 65 },
    { "year": 2025, "count": 72 }
  ],
  "students_by_status": [
    { "status": "재학", "count": 450 },
    { "status": "휴학", "count": 30 },
    { "status": "졸업", "count": 200 }
  ],
  "budget_execution": {
    "total_budget": 1600000000,
    "executed_amount": 1283500000,
    "pending_amount": 165000000,
    "execution_rate": 80.22
  }
}
```

### B. 사용된 공통 모듈 목록

#### 백엔드
- `apps/core/repositories.py`: BaseRepository
- `apps/dashboard/repositories.py`: 도메인 Repository들
- `apps/dashboard/services/summary_generator.py`: DashboardSummaryService
- `apps/dashboard/serializers.py`: DashboardSummarySerializer
- `apps/users/middleware.py`: 인증 미들웨어

#### 프론트엔드
- `src/api/dashboardAPI.js`: API 클라이언트
- `src/hooks/useApi.js`: API 호출 훅
- `src/components/common/*`: 공통 UI 컴포넌트
- `src/components/layout/MainLayout.jsx`: 레이아웃
- `src/store/authStore.js`: 인증 상태 관리

### C. 참고 자료

- [Recharts 공식 문서](https://recharts.org/)
- [Django REST Framework 테스트 가이드](https://www.django-rest-framework.org/api-guide/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Vitest 문서](https://vitest.dev/)

---

**작성 완료일:** 2025-11-13
**최종 검토자:** CTO
**승인 상태:** Ready for Implementation
