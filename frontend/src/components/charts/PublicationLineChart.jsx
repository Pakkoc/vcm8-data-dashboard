import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
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
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
