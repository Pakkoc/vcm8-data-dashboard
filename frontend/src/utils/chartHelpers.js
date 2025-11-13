/**
 * 차트 관련 유틸리티 함수 모음
 */

/**
 * 숫자를 천 단위 콤마 형식으로 변환
 * @param {number} value - 변환할 숫자
 * @returns {string} - 포맷된 문자열
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined) return '0';
  return new Intl.NumberFormat('ko-KR').format(value);
};

/**
 * 금액을 억원 단위로 변환
 * @param {number} value - 원 단위 금액
 * @returns {string} - 억원 단위 문자열
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0억원';
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
  neutral: '#6b7280',
};

/**
 * 파이 차트용 색상 배열
 */
export const PIE_COLORS = [
  '#3b82f6', // Blue
  '#8b5cf6', // Purple
  '#10b981', // Green
  '#f59e0b', // Amber
  '#ef4444', // Red
  '#06b6d4', // Cyan
  '#ec4899', // Pink
];

/**
 * 퍼센트 포맷팅
 * @param {number} value - 퍼센트 값
 * @param {number} decimals - 소수점 자리수
 * @returns {string} - 포맷된 퍼센트 문자열
 */
export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%';
  return `${value.toFixed(decimals)}%`;
};
