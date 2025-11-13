from typing import List
from rest_framework.exceptions import ValidationError
import pandas as pd


class DataSchemaValidator:
    """엑셀 데이터 스키마 검증"""

    STUDENT_REQUIRED_COLUMNS = [
        '학번',
        '이름',
        '단과대학',
        '학과',
        '과정구분',
        '학적상태',
    ]

    DEPARTMENT_KPI_REQUIRED_COLUMNS = [
        '단과대학',
        '학과',
        '평가년도',
        '졸업생취업률',
        '전임교원수',
    ]

    PUBLICATION_REQUIRED_COLUMNS = [
        '논문ID',
        '게재일',  # CSV 파일에서는 '게재일'로 사용
        '단과대학',
        '학과',
        '논문제목',
    ]

    RESEARCH_PROJECT_REQUIRED_COLUMNS = [
        '과제번호',
        '과제명',
        '연구책임자',
        '소속학과',  # CSV 파일에서는 '소속학과'로 사용
    ]

    PROJECT_EXPENSE_REQUIRED_COLUMNS = [
        '과제번호',
        '집행ID',
        '집행일자',
        '집행항목',
        '집행금액',
        '상태',  # CSV 파일에서는 '상태'로 사용
    ]

    @staticmethod
    def validate_columns(
        df: pd.DataFrame, required_columns: List[str], sheet_name: str
    ) -> None:
        """필수 컬럼 존재 여부 검증"""
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValidationError(
                f"{sheet_name} 시트: 필수 컬럼이 누락되었습니다: {', '.join(missing)}"
            )

    @staticmethod
    def validate_not_empty(df: pd.DataFrame, sheet_name: str) -> None:
        """데이터가 비어있지 않은지 검증"""
        if df.empty:
            raise ValidationError(f"{sheet_name} 시트: 데이터가 없습니다.")

    @staticmethod
    def validate_date_format(df: pd.DataFrame, column_name: str, sheet_name: str) -> None:
        """날짜 형식 검증"""
        try:
            pd.to_datetime(df[column_name], errors='coerce')
        except Exception as e:
            raise ValidationError(
                f"{sheet_name} 시트: '{column_name}' 컬럼의 날짜 형식이 올바르지 않습니다: {str(e)}"
            )

    @staticmethod
    def validate_numeric(
        df: pd.DataFrame, column_name: str, sheet_name: str, allow_null: bool = True
    ) -> None:
        """숫자 형식 검증"""
        if not allow_null and df[column_name].isnull().any():
            raise ValidationError(
                f"{sheet_name} 시트: '{column_name}' 컬럼에 빈 값이 있습니다."
            )

        non_null_values = df[column_name].dropna()
        if not non_null_values.empty:
            try:
                pd.to_numeric(non_null_values, errors='raise')
            except Exception as e:
                raise ValidationError(
                    f"{sheet_name} 시트: '{column_name}' 컬럼이 숫자가 아닙니다: {str(e)}"
                )
