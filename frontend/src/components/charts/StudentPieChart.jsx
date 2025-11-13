import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import EmptyState from '../common/EmptyState';
import { PIE_COLORS, formatNumber } from '../../utils/chartHelpers';

const StudentPieChart = ({ data }) => {
  if (!data || data.length === 0) {
    return <EmptyState message="학생 현황 데이터가 없습니다." />;
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const itemData = payload[0];
    const total = itemData.payload.total;
    const percentage = ((itemData.value / total) * 100).toFixed(1);

    return (
      <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
        <p className="font-semibold text-sm mb-1">{itemData.name}</p>
        <p className="text-xs text-gray-600">
          인원: {formatNumber(itemData.value)}명 ({percentage}%)
        </p>
      </div>
    );
  };

  // 전체 학생 수 계산
  const total = data.reduce((sum, item) => sum + item.count, 0);

  // 차트 데이터에 total 추가
  const chartData = data.map((item) => ({
    name: item.status,
    value: item.count,
    total: total,
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
            <Cell
              key={`cell-${index}`}
              fill={PIE_COLORS[index % PIE_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: '12px' }} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default StudentPieChart;
