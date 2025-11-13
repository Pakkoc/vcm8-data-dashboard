import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import EmptyState from '../common/EmptyState';
import { CHART_COLORS, formatNumber } from '../../utils/chartHelpers';

const PerformanceBarChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <EmptyState message="학과별 성과 데이터가 없습니다." />;
  }

  // 차트 표시용 데이터 변환
  const chartData = data.map((item) => ({
    name: item.department_name,
    학생수: item.student_count,
    논문수: item.publication_count,
    과제수: item.project_count,
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
