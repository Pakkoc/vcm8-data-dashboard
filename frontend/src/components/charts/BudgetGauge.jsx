import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Label,
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
    { value: 100 - execution_rate, fill: '#e5e7eb' },
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
              style={{
                fontSize: '24px',
                fontWeight: 'bold',
                fill: CHART_COLORS.success,
              }}
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
