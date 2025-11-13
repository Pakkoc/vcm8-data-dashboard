import pandas as pd
from typing import Dict
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.dashboard.repositories import (
    CollegeRepository,
    DepartmentRepository,
    StudentRepository,
    DepartmentKPIRepository,
    PublicationRepository,
    ResearchProjectRepository,
    ProjectExpenseRepository,
)
from apps.dashboard.models import (
    Student,
    DepartmentKPI,
    Publication,
    ResearchProject,
    ProjectExpense,
)
from .validators import DataSchemaValidator


class ExcelImportService:
    """엑셀 파일 Import 비즈니스 로직"""

    def __init__(self):
        self.college_repo = CollegeRepository()
        self.department_repo = DepartmentRepository()
        self.student_repo = StudentRepository()
        self.kpi_repo = DepartmentKPIRepository()
        self.publication_repo = PublicationRepository()
        self.project_repo = ResearchProjectRepository()
        self.expense_repo = ProjectExpenseRepository()
        self.validator = DataSchemaValidator()

    @transaction.atomic
    def import_from_excel(self, file_path: str) -> Dict[str, int]:
        """
        엑셀 파일을 읽어 데이터베이스에 저장

        Returns:
            각 테이블별 삽입된 레코드 수
        """
        # 1. 엑셀 파일 읽기
        print(f"[ExcelImporter] 파일 읽기 시작: {file_path}")
        dataframes = self._read_excel_file(file_path)
        print(f"[ExcelImporter] 읽은 데이터프레임: {list(dataframes.keys())}")
        for key, df in dataframes.items():
            print(f"[ExcelImporter]   - {key}: {len(df)}행, 컬럼: {list(df.columns)}")

        # 2. 데이터 검증
        print("[ExcelImporter] 데이터 검증 시작...")
        try:
            self._validate_data(dataframes)
            print("[ExcelImporter] 데이터 검증 완료")
        except Exception as e:
            print(f"[ExcelImporter] ❌ 데이터 검증 실패: {e}")
            raise

        # 3. 기존 데이터 삭제 (선택적)
        # CSV 파일인 경우: 해당 테이블만 삭제
        # Excel 파일인 경우: 모든 데이터 삭제
        is_csv = file_path.lower().endswith('.csv')
        if is_csv:
            print(f"[ExcelImporter] CSV 모드: {list(dataframes.keys())} 테이블만 삭제...")
            self._delete_specific_data(dataframes.keys())
        else:
            print("[ExcelImporter] Excel 모드: 기존 데이터 전체 삭제...")
            self._delete_existing_data()

        # 4. 단과대학 및 학과 추출 및 저장
        print("[ExcelImporter] 단과대학 및 학과 저장...")
        college_mapping, department_mapping = self._save_colleges_and_departments(
            dataframes
        )
        print(f"[ExcelImporter] 저장 완료 - 단과대학: {len(college_mapping)}, 학과: {len(department_mapping)}")

        # 5. 각 테이블 데이터 저장
        result = {
            'colleges': len(college_mapping),
            'departments': len(department_mapping),
            'students': 0,
            'department_kpis': 0,
            'publications': 0,
            'research_projects': 0,
            'project_expenses': 0,
        }

        if 'students' in dataframes:
            print("[ExcelImporter] 학생 데이터 저장 중...")
            result['students'] = self._save_students(
                dataframes['students'], department_mapping
            )
            print(f"[ExcelImporter] 학생 데이터 {result['students']}개 저장 완료")

        if 'kpis' in dataframes:
            print("[ExcelImporter] KPI 데이터 저장 중...")
            result['department_kpis'] = self._save_kpis(
                dataframes['kpis'], department_mapping
            )
            print(f"[ExcelImporter] KPI 데이터 {result['department_kpis']}개 저장 완료")

        if 'publications' in dataframes:
            print("[ExcelImporter] 논문 데이터 저장 중...")
            result['publications'] = self._save_publications(
                dataframes['publications'], department_mapping
            )
            print(f"[ExcelImporter] 논문 데이터 {result['publications']}개 저장 완료")

        if 'projects' in dataframes:
            print("[ExcelImporter] 프로젝트 데이터 저장 중...")
            projects_count, expenses_count = self._save_projects_and_expenses(
                dataframes['projects'], department_mapping
            )
            result['research_projects'] = projects_count
            result['project_expenses'] = expenses_count
            print(f"[ExcelImporter] 프로젝트 {projects_count}개, 지출 {expenses_count}개 저장 완료")

        print(f"[ExcelImporter] ✅ Import 완료: {result}")
        return result

    @transaction.atomic
    def import_from_multiple_files(self, file_paths: list) -> Dict[str, int]:
        """
        여러 파일을 동시에 읽어 데이터베이스에 저장
        순서 상관없이 업로드 가능

        Returns:
            각 테이블별 삽입된 레코드 수
        """
        print(f"[ExcelImporter] 배치 Import 시작: {len(file_paths)}개 파일")

        # 1. 모든 파일 읽기
        all_dataframes = {}
        for file_path in file_paths:
            print(f"[ExcelImporter] 파일 읽기: {file_path}")
            dataframes = self._read_excel_file(file_path)
            print(f"[ExcelImporter]   읽은 데이터프레임: {list(dataframes.keys())}")

            # 같은 타입의 데이터프레임을 합치기
            for key, df in dataframes.items():
                if key in all_dataframes:
                    # 기존 데이터에 추가
                    all_dataframes[key] = pd.concat([all_dataframes[key], df], ignore_index=True)
                    print(f"[ExcelImporter]   - {key}: {len(df)}행 추가 (총 {len(all_dataframes[key])}행)")
                else:
                    all_dataframes[key] = df
                    print(f"[ExcelImporter]   - {key}: {len(df)}행")

        print(f"[ExcelImporter] 전체 데이터프레임: {list(all_dataframes.keys())}")
        for key, df in all_dataframes.items():
            print(f"[ExcelImporter]   - {key}: 총 {len(df)}행")

        # 2. 데이터 검증
        print("[ExcelImporter] 데이터 검증 시작...")
        try:
            self._validate_data(all_dataframes)
            print("[ExcelImporter] 데이터 검증 완료")
        except Exception as e:
            print(f"[ExcelImporter] ❌ 데이터 검증 실패: {e}")
            raise

        # 3. 기존 데이터 전체 삭제
        print("[ExcelImporter] 기존 데이터 전체 삭제...")
        self._delete_existing_data()

        # 4. Pass 1: 단과대학 및 학과 추출 및 저장
        print("[ExcelImporter] Pass 1: 단과대학 및 학과 저장...")
        college_mapping, department_mapping = self._save_colleges_and_departments(
            all_dataframes
        )
        print(f"[ExcelImporter] 저장 완료 - 단과대학: {len(college_mapping)}, 학과: {len(department_mapping)}")

        # 5. Pass 2: 각 테이블 데이터 저장
        result = {
            'colleges': len(college_mapping),
            'departments': len(department_mapping),
            'students': 0,
            'department_kpis': 0,
            'publications': 0,
            'research_projects': 0,
            'project_expenses': 0,
        }

        if 'students' in all_dataframes:
            print("[ExcelImporter] Pass 2: 학생 데이터 저장 중...")
            result['students'] = self._save_students(
                all_dataframes['students'], department_mapping
            )
            print(f"[ExcelImporter] 학생 데이터 {result['students']}개 저장 완료")

        if 'kpis' in all_dataframes:
            print("[ExcelImporter] Pass 2: KPI 데이터 저장 중...")
            result['department_kpis'] = self._save_kpis(
                all_dataframes['kpis'], department_mapping
            )
            print(f"[ExcelImporter] KPI 데이터 {result['department_kpis']}개 저장 완료")

        if 'publications' in all_dataframes:
            print("[ExcelImporter] Pass 2: 논문 데이터 저장 중...")
            result['publications'] = self._save_publications(
                all_dataframes['publications'], department_mapping
            )
            print(f"[ExcelImporter] 논문 데이터 {result['publications']}개 저장 완료")

        if 'projects' in all_dataframes:
            print("[ExcelImporter] Pass 2: 프로젝트 데이터 저장 중...")
            projects_count, expenses_count = self._save_projects_and_expenses(
                all_dataframes['projects'], department_mapping
            )
            result['research_projects'] = projects_count
            result['project_expenses'] = expenses_count
            print(f"[ExcelImporter] 프로젝트 {projects_count}개, 지출 {expenses_count}개 저장 완료")

        print(f"[ExcelImporter] ✅ 배치 Import 완료: {result}")
        return result

    def _normalize_column_name(self, col_name: str) -> str:
        """
        컬럼명 정규화
        - 모든 공백 제거 (단어 사이 공백 포함)
        - 괄호와 괄호 안의 내용 제거
        """
        import re
        # 괄호와 괄호 안의 내용 제거
        col_name = re.sub(r'\s*\([^)]*\)', '', col_name)
        # 모든 공백 제거 (단어 사이 공백도 포함)
        col_name = re.sub(r'\s+', '', col_name)
        return col_name

    def _normalize_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame의 모든 컬럼명 정규화"""
        df.columns = [self._normalize_column_name(col) for col in df.columns]
        return df

    def _read_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """엑셀 파일 읽기"""
        try:
            # CSV 파일인 경우
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                # 컬럼명 정규화
                df = self._normalize_dataframe_columns(df)

                # CSV 파일명으로 시트 이름 판단
                if 'student' in file_path.lower():
                    return {'students': df}
                elif 'kpi' in file_path.lower():
                    return {'kpis': df}
                elif 'publication' in file_path.lower():
                    return {'publications': df}
                elif 'project' in file_path.lower() or 'research' in file_path.lower():
                    return {'projects': df}
                else:
                    return {'data': df}

            # 엑셀 파일인 경우 - 여러 시트 읽기
            excel_file = pd.ExcelFile(file_path)
            dataframes = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                # 컬럼명 정규화
                df = self._normalize_dataframe_columns(df)

                # 시트 이름으로 데이터 종류 판단
                sheet_lower = sheet_name.lower()
                if 'student' in sheet_lower or '학생' in sheet_lower:
                    dataframes['students'] = df
                elif 'kpi' in sheet_lower or '성과' in sheet_lower:
                    dataframes['kpis'] = df
                elif 'publication' in sheet_lower or '논문' in sheet_lower:
                    dataframes['publications'] = df
                elif 'project' in sheet_lower or '과제' in sheet_lower or '연구' in sheet_lower:
                    dataframes['projects'] = df

            return dataframes

        except Exception as e:
            raise ValidationError(f"엑셀 파일을 읽을 수 없습니다: {str(e)}")

    def _validate_data(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """모든 데이터프레임 검증"""
        if 'students' in dataframes:
            df = dataframes['students']
            self.validator.validate_not_empty(df, 'student_roster')
            self.validator.validate_columns(
                df, self.validator.STUDENT_REQUIRED_COLUMNS, 'student_roster'
            )

        if 'kpis' in dataframes:
            df = dataframes['kpis']
            self.validator.validate_not_empty(df, 'department_kpi')
            self.validator.validate_columns(
                df, self.validator.DEPARTMENT_KPI_REQUIRED_COLUMNS, 'department_kpi'
            )

        if 'publications' in dataframes:
            df = dataframes['publications']
            self.validator.validate_not_empty(df, 'publication_list')
            self.validator.validate_columns(
                df, self.validator.PUBLICATION_REQUIRED_COLUMNS, 'publication_list'
            )

        if 'projects' in dataframes:
            df = dataframes['projects']
            self.validator.validate_not_empty(df, 'research_project_data')
            self.validator.validate_columns(
                df, self.validator.RESEARCH_PROJECT_REQUIRED_COLUMNS, 'research_project_data'
            )

    def _delete_existing_data(self) -> None:
        """기존 데이터 삭제 (외래 키 순서 고려)"""
        self.expense_repo.delete_all()
        self.project_repo.delete_all()
        self.publication_repo.delete_all()
        self.kpi_repo.delete_all()
        self.student_repo.delete_all()
        self.department_repo.delete_all()
        self.college_repo.delete_all()

    def _delete_specific_data(self, data_types: list) -> None:
        """특정 테이블만 삭제 (CSV 개별 업로드용)"""
        for data_type in data_types:
            if data_type == 'students':
                print("[ExcelImporter]   - 학생 데이터 삭제")
                self.student_repo.delete_all()
            elif data_type == 'kpis':
                print("[ExcelImporter]   - KPI 데이터 삭제")
                self.kpi_repo.delete_all()
            elif data_type == 'publications':
                print("[ExcelImporter]   - 논문 데이터 삭제")
                self.publication_repo.delete_all()
            elif data_type == 'projects':
                print("[ExcelImporter]   - 프로젝트 및 지출 데이터 삭제")
                self.expense_repo.delete_all()
                self.project_repo.delete_all()

    def _save_colleges_and_departments(
        self, dataframes: Dict[str, pd.DataFrame]
    ) -> tuple:
        """
        모든 데이터프레임에서 단과대학과 학과 추출 후 저장

        Returns:
            (college_mapping, department_mapping): 이름 -> ID 매핑 딕셔너리
        """
        college_names = set()
        department_info = set()  # (college_name, department_name) 튜플

        # 모든 시트에서 단과대학과 학과 추출
        for df in dataframes.values():
            if '단과대학' in df.columns and '학과' in df.columns:
                for _, row in df.iterrows():
                    college_name = str(row['단과대학']).strip()
                    dept_name = str(row['학과']).strip()
                    college_names.add(college_name)
                    department_info.add((college_name, dept_name))

        # 단과대학 저장
        college_mapping = {}
        for college_name in college_names:
            college = self.college_repo.get_or_create_by_name(college_name)
            college_mapping[college_name] = college.id

        # 학과 저장
        department_mapping = {}
        for college_name, dept_name in department_info:
            college_id = college_mapping[college_name]
            college = self.college_repo.get_by_id(college_id)
            department = self.department_repo.get_or_create_by_college_and_name(
                college, dept_name
            )
            department_mapping[f"{college_name}|{dept_name}"] = department.id

        # 매핑이 비어있는 경우 (예: research_project_data.csv처럼 단과대학 정보가 없는 경우)
        # 데이터베이스에서 기존 학과들을 모두 가져와서 매핑 생성
        if not department_mapping:
            print("[ExcelImporter]   단과대학 정보 없음 - 기존 학과 매핑 사용")
            from apps.dashboard.models import Department
            departments = Department.objects.select_related('college').all()
            for dept in departments:
                key = f"{dept.college.name}|{dept.name}"
                department_mapping[key] = dept.id
                if dept.college.name not in college_mapping:
                    college_mapping[dept.college.name] = dept.college.id
            print(f"[ExcelImporter]   기존 매핑: {len(college_mapping)}개 단과대학, {len(department_mapping)}개 학과")

        return college_mapping, department_mapping

    def _save_students(
        self, df: pd.DataFrame, dept_mapping: dict
    ) -> int:
        """학생 데이터 저장"""
        students = []
        for _, row in df.iterrows():
            key = f"{row['단과대학']}|{row['학과']}"
            if key not in dept_mapping:
                continue

            student = Student(
                student_id_number=str(row['학번']),
                name=str(row['이름']),
                department_id=dept_mapping[key],
                grade=int(row['학년']) if pd.notna(row.get('학년')) else None,
                program_level=str(row['과정구분']),
                status=str(row['학적상태']),
                gender=str(row['성별']) if pd.notna(row.get('성별')) else None,
                admission_year=int(row['입학년도']) if pd.notna(row.get('입학년도')) else None,
                advisor_name=str(row['지도교수']) if pd.notna(row.get('지도교수')) else None,
                email=str(row['이메일']) if pd.notna(row.get('이메일')) else None,
            )
            students.append(student)

        self.student_repo.bulk_create(students)
        return len(students)

    def _save_kpis(self, df: pd.DataFrame, dept_mapping: dict) -> int:
        """학과 KPI 데이터 저장"""
        kpis = []
        for _, row in df.iterrows():
            key = f"{row['단과대학']}|{row['학과']}"
            if key not in dept_mapping:
                continue

            kpi = DepartmentKPI(
                department_id=dept_mapping[key],
                evaluation_year=int(row['평가년도']),
                employment_rate=float(row['졸업생취업률']) if pd.notna(row.get('졸업생취업률')) else None,
                full_time_faculty_count=int(row['전임교원수']) if pd.notna(row.get('전임교원수')) else None,
                visiting_faculty_count=int(row['초빙교원수']) if pd.notna(row.get('초빙교원수')) else None,
                tech_transfer_income=float(row['연간기술이전수입액(억)']) if pd.notna(row.get('연간기술이전수입액(억)')) else None,
                international_conferences_count=int(row['국제학술대회개최횟수']) if pd.notna(row.get('국제학술대회개최횟수')) else None,
            )
            kpis.append(kpi)

        self.kpi_repo.bulk_create(kpis)
        return len(kpis)

    def _save_publications(self, df: pd.DataFrame, dept_mapping: dict) -> int:
        """논문 데이터 저장"""
        publications = []
        for _, row in df.iterrows():
            key = f"{row['단과대학']}|{row['학과']}"
            if key not in dept_mapping:
                continue

            # 게재일 또는 게재일자 컬럼 지원
            pub_date_col = '게재일' if '게재일' in row else '게재일자'

            publication = Publication(
                publication_id_str=str(row['논문ID']) if pd.notna(row.get('논문ID')) else None,
                publication_date=pd.to_datetime(row[pub_date_col]).date(),
                department_id=dept_mapping[key],
                title=str(row['논문제목']),
                # '주저자' 또는 '제1저자' 컬럼 지원
                primary_author=str(row.get('주저자', row.get('제1저자', ''))) if pd.notna(row.get('주저자', row.get('제1저자'))) else None,
                # '참여저자' 또는 '참여저자목록' 컬럼 지원
                contributing_authors=str(row.get('참여저자', row.get('참여저자목록', ''))) if pd.notna(row.get('참여저자', row.get('참여저자목록'))) else None,
                journal_name=str(row['학술지명']) if pd.notna(row.get('학술지명')) else None,
                # '저널등급' 또는 '학술지등급' 컬럼 지원
                journal_rank=str(row.get('저널등급', row.get('학술지등급', ''))) if pd.notna(row.get('저널등급', row.get('학술지등급'))) else None,
                # 'ImpactFactor' (정규화된) 또는 'IF' 컬럼 지원
                impact_factor=float(row.get('ImpactFactor', row.get('IF', 0))) if pd.notna(row.get('ImpactFactor', row.get('IF'))) else None,
                is_project_linked=bool(row.get('과제연계여부', 'N') == 'Y') if pd.notna(row.get('과제연계여부')) else False,
            )
            publications.append(publication)

        self.publication_repo.bulk_create(publications)
        return len(publications)

    def _save_projects_and_expenses(
        self, df: pd.DataFrame, dept_mapping: dict
    ) -> tuple:
        """연구 과제 및 집행 내역 저장"""
        # 과제번호별로 그룹화
        project_groups = df.groupby('과제번호')

        projects = []
        expenses = []
        project_id_mapping = {}

        for project_number, group in project_groups:
            first_row = group.iloc[0]

            # 단과대학과 학과가 별도 컬럼인 경우
            if '단과대학' in first_row and '학과' in first_row:
                key = f"{first_row['단과대학']}|{first_row['학과']}"
            # 소속학과만 있는 경우 (학과명만으로 검색)
            elif '소속학과' in first_row:
                dept_name = first_row['소속학과']
                # 학과명으로 매핑 찾기
                key = None
                for k in dept_mapping.keys():
                    if k.endswith(f"|{dept_name}"):
                        key = k
                        break
                if not key:
                    continue
            else:
                continue

            if key not in dept_mapping:
                continue

            # 연구 과제 저장
            project = ResearchProject(
                project_number=str(project_number),
                name=str(first_row['과제명']),
                principal_investigator=str(first_row['연구책임자']) if pd.notna(first_row.get('연구책임자')) else None,
                department_id=dept_mapping[key],
                funding_agency=str(first_row['지원기관']) if pd.notna(first_row.get('지원기관')) else None,
                total_funding_amount=int(first_row['총연구비']) if pd.notna(first_row.get('총연구비')) else None,
            )
            projects.append(project)

        # 프로젝트 bulk create
        created_projects = self.project_repo.bulk_create(projects)

        # 프로젝트 번호로 ID 매핑 생성
        for project in created_projects:
            project_id_mapping[project.project_number] = project.id

        # 집행 내역 저장
        for project_number, group in project_groups:
            if project_number not in project_id_mapping:
                continue

            project_id = project_id_mapping[project_number]

            for _, row in group.iterrows():
                if pd.notna(row.get('집행ID')):
                    expense = ProjectExpense(
                        execution_id=str(row['집행ID']),
                        project_id=project_id,
                        execution_date=pd.to_datetime(row['집행일자']).date(),
                        item=str(row['집행항목']),
                        amount=int(row['집행금액']),
                        status=str(row.get('상태', row.get('처리상태', ''))),  # '상태' 또는 '처리상태' 컬럼 지원
                        notes=str(row['비고']) if pd.notna(row.get('비고')) else None,
                    )
                    expenses.append(expense)

        if expenses:
            self.expense_repo.bulk_create(expenses)

        return len(projects), len(expenses)
