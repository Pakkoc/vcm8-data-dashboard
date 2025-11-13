# 공통 모듈 작업 계획 (Common Modules Implementation Plan)

**작성일:** 2025-11-13
**작성자:** Development Team
**프로젝트:** 대학교 데이터 시각화 대시보드 MVP

---

## 문서 목적

본 문서는 페이지 단위 개발을 시작하기 전에 구축해야 할 공통 모듈 및 인프라를 정의합니다. 모든 공통 모듈은 병렬 개발 시 코드 충돌을 최소화하고, TDD 방식의 개발 환경을 지원하도록 설계됩니다.

**핵심 원칙:**
- 오버엔지니어링 금지: PRD, 유스케이스, 데이터베이스 스키마에 명시된 기능만 구현
- 테스트 우선: 모든 공통 모듈은 단위 테스트 가능하도록 설계
- 명확한 책임 분리: 각 모듈은 단일 책임 원칙(SRP) 준수

---

## 1. 프로젝트 초기 환경 설정

### 1.1 백엔드 프로젝트 초기화

**목적:** Django + DRF 프로젝트의 기본 구조와 설정 파일 생성

**작업 내용:**
- Django 프로젝트 생성 (`dashboard_project`)
- Django REST Framework 설치 및 설정
- Supabase PostgreSQL 연결 설정
- 환경 변수 관리 설정 (`.env` 파일)
- CORS 설정 (프론트엔드와의 통신)
- 기본 미들웨어 설정

**산출물:**
```
/backend
├── dashboard_project/
│   ├── __init__.py
│   ├── settings.py        # 환경별 설정 (dev, prod)
│   ├── urls.py            # 전역 URL 라우팅
│   ├── wsgi.py
│   └── asgi.py
├── .env.example           # 환경 변수 템플릿
├── requirements.txt       # Python 의존성
└── manage.py
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 2시간

---

### 1.2 프론트엔드 프로젝트 초기화

**목적:** React + Vite 프로젝트의 기본 구조 생성

**작업 내용:**
- Vite + React 프로젝트 생성
- 필수 라이브러리 설치
  - React Router DOM (라우팅)
  - Axios (HTTP 클라이언트)
  - Recharts (차트 라이브러리)
  - Zustand 또는 Jotai (상태 관리)
  - TailwindCSS (스타일링)
- 폴더 구조 생성 (architecture.md 참조)
- 환경 변수 설정 (`.env`)

**산출물:**
```
/frontend
├── public/
├── src/
│   ├── api/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── store/
│   ├── utils/
│   ├── App.jsx
│   └── main.jsx
├── .env.example
├── package.json
├── vite.config.js
└── tailwind.config.js
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 2시간

---

## 2. 백엔드 공통 모듈

### 2.1 인증/인가 시스템 (Authentication & Authorization)

**목적:** Supabase Auth 기반 사용자 인증 및 권한 관리

**참조 유스케이스:** UC-001 (로그인), UC-002 (로그아웃)

**구현 범위:**

#### 2.1.1 User Profile 모델
```python
# apps/users/models.py

class UserRole(models.TextChoices):
    ADMIN = 'admin', '관리자'
    GENERAL = 'general', '일반 사용자'

class Profile(models.Model):
    """Supabase Auth 사용자와 연결되는 프로필"""
    id = models.UUIDField(primary_key=True)  # Supabase user.id
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.GENERAL
    )
    username = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 2.1.2 인증 미들웨어
```python
# apps/users/middleware.py

class SupabaseAuthMiddleware:
    """JWT 토큰 검증 및 사용자 정보 추출"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Authorization 헤더에서 JWT 토큰 추출
        # Supabase JWT 검증
        # request.user에 사용자 정보 저장
        pass
```

#### 2.1.3 권한 검사 데코레이터
```python
# apps/users/decorators.py

def admin_required(view_func):
    """관리자 권한 필수 데코레이터"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.profile.role == UserRole.ADMIN:
            return JsonResponse({'error': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper
```

**테스트 케이스:**
- JWT 토큰 검증 성공/실패
- 만료된 토큰 처리
- 권한별 접근 제어 (admin vs general)
- 인증 없이 보호된 엔드포인트 접근 시도

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 4시간

---

### 2.2 데이터베이스 모델 (Database Models)

**목적:** database.md에 정의된 모든 테이블을 Django ORM 모델로 구현

**참조 문서:** `/docs/database.md`

**구현 범위:**

#### 2.2.1 핵심 엔티티 모델
```python
# apps/dashboard/models.py

class College(models.Model):
    """단과대학 정보"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Department(models.Model):
    """학과 정보"""
    id = models.BigAutoField(primary_key=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['college', 'name']]

class AcademicProgram(models.TextChoices):
    BACHELOR = '학사', '학사'
    MASTER = '석사', '석사'
    DOCTORAL = '박사', '박사'

class AcademicStatus(models.TextChoices):
    ENROLLED = '재학', '재학'
    LEAVE = '휴학', '휴학'
    GRADUATED = '졸업', '졸업'

class Student(models.Model):
    """학생 명단"""
    id = models.BigAutoField(primary_key=True)
    student_id_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    grade = models.SmallIntegerField(null=True)
    program_level = models.CharField(max_length=10, choices=AcademicProgram.choices)
    status = models.CharField(max_length=10, choices=AcademicStatus.choices)
    gender = models.CharField(max_length=1, null=True)
    admission_year = models.IntegerField(null=True)
    advisor_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 2.2.2 성과 데이터 모델
```python
class DepartmentKPI(models.Model):
    """학과별 핵심 성과 지표"""
    id = models.BigAutoField(primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    evaluation_year = models.IntegerField()
    employment_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    full_time_faculty_count = models.IntegerField(null=True)
    visiting_faculty_count = models.IntegerField(null=True)
    tech_transfer_income = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    international_conferences_count = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['department', 'evaluation_year']]

class Publication(models.Model):
    """논문 목록"""
    id = models.BigAutoField(primary_key=True)
    publication_id_str = models.CharField(max_length=100, unique=True, null=True)
    publication_date = models.DateField()
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    title = models.TextField()
    primary_author = models.CharField(max_length=100, null=True)
    contributing_authors = models.TextField(null=True)
    journal_name = models.TextField(null=True)
    journal_rank = models.CharField(max_length=50, null=True)
    impact_factor = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    is_project_linked = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ResearchProject(models.Model):
    """연구 과제 정보"""
    id = models.BigAutoField(primary_key=True)
    project_number = models.CharField(max_length=100, unique=True)
    name = models.TextField()
    principal_investigator = models.CharField(max_length=100, null=True)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    funding_agency = models.CharField(max_length=255, null=True)
    total_funding_amount = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProjectStatus(models.TextChoices):
    PROCESSING = '처리중', '처리중'
    COMPLETED = '집행완료', '집행완료'
    REJECTED = '반려', '반려'

class ProjectExpense(models.Model):
    """연구 과제 집행 내역"""
    id = models.BigAutoField(primary_key=True)
    execution_id = models.CharField(max_length=100, unique=True)
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE)
    execution_date = models.DateField()
    item = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=ProjectStatus.choices)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**마이그레이션 파일:**
- 초기 마이그레이션 생성
- 인덱스 추가 (database.md 참조)

**테스트 케이스:**
- 모델 생성/조회/수정/삭제
- 외래 키 제약조건 검증
- Unique 제약조건 검증
- Enum 타입 검증

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 3시간

---

### 2.3 Repository 레이어 (Data Access Layer)

**목적:** 데이터베이스 접근 로직을 캡슐화하여 비즈니스 로직과 분리

**참조 문서:** `/docs/structure.md`

**구현 범위:**

#### 2.3.1 Base Repository
```python
# apps/core/repositories.py

from typing import Generic, TypeVar, Type, List, Optional
from django.db import models

T = TypeVar('T', bound=models.Model)

class BaseRepository(Generic[T]):
    """모든 Repository의 기본 클래스"""

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """ID로 단일 객체 조회"""
        try:
            return self.model_class.objects.get(pk=id)
        except self.model_class.DoesNotExist:
            return None

    def get_all(self) -> List[T]:
        """모든 객체 조회"""
        return list(self.model_class.objects.all())

    def create(self, **kwargs) -> T:
        """객체 생성"""
        return self.model_class.objects.create(**kwargs)

    def bulk_create(self, objects: List[T]) -> List[T]:
        """대량 객체 생성"""
        return self.model_class.objects.bulk_create(objects)

    def delete_all(self) -> None:
        """모든 객체 삭제"""
        self.model_class.objects.all().delete()
```

#### 2.3.2 Domain-Specific Repositories
```python
# apps/dashboard/repositories.py

class StudentRepository(BaseRepository[Student]):
    """학생 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(Student)

    def count_by_department(self, department_id: int) -> int:
        """특정 학과의 학생 수 조회"""
        return self.model_class.objects.filter(department_id=department_id).count()

    def count_by_status(self) -> dict:
        """학적 상태별 학생 수 집계"""
        from django.db.models import Count
        result = self.model_class.objects.values('status').annotate(count=Count('id'))
        return {item['status']: item['count'] for item in result}

class PublicationRepository(BaseRepository[Publication]):
    """논문 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(Publication)

    def count_by_year(self) -> List[dict]:
        """연도별 논문 수 집계"""
        from django.db.models import Count
        from django.db.models.functions import ExtractYear

        return list(
            self.model_class.objects
            .annotate(year=ExtractYear('publication_date'))
            .values('year')
            .annotate(count=Count('id'))
            .order_by('year')
        )

    def count_by_department(self, department_id: int) -> int:
        """특정 학과의 논문 수 조회"""
        return self.model_class.objects.filter(department_id=department_id).count()

class ProjectExpenseRepository(BaseRepository[ProjectExpense]):
    """연구 과제 집행 데이터 접근 레이어"""

    def __init__(self):
        super().__init__(ProjectExpense)

    def sum_by_status(self, status: str) -> int:
        """특정 상태의 총 집행 금액"""
        from django.db.models import Sum
        result = self.model_class.objects.filter(status=status).aggregate(total=Sum('amount'))
        return result['total'] or 0

    def calculate_execution_rate(self) -> float:
        """전체 예산 집행률 계산"""
        from django.db.models import Sum
        total_budget = ResearchProject.objects.aggregate(total=Sum('total_funding_amount'))['total'] or 0
        executed_amount = self.sum_by_status(ProjectStatus.COMPLETED)

        if total_budget == 0:
            return 0.0
        return (executed_amount / total_budget) * 100

class CollegeRepository(BaseRepository[College]):
    def __init__(self):
        super().__init__(College)

    def get_or_create_by_name(self, name: str) -> College:
        """이름으로 조회하거나 생성"""
        college, created = self.model_class.objects.get_or_create(name=name)
        return college

class DepartmentRepository(BaseRepository[Department]):
    def __init__(self):
        super().__init__(Department)

    def get_or_create_by_college_and_name(self, college: College, name: str) -> Department:
        """단과대학과 이름으로 조회하거나 생성"""
        department, created = self.model_class.objects.get_or_create(
            college=college,
            name=name
        )
        return department
```

**테스트 케이스:**
- 각 Repository 메소드별 단위 테스트
- 트랜잭션 롤백 테스트
- 대량 데이터 처리 성능 테스트

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 4시간

---

### 2.4 Excel Import Service (엑셀 데이터 처리)

**목적:** 업로드된 엑셀 파일을 파싱하고 데이터베이스에 저장

**참조 유스케이스:** UC-002 (엑셀 파일 업로드)

**참조 데이터:** `/docs/input_data/*.csv`

**구현 범위:**

#### 2.4.1 Data Schema Validator
```python
# apps/dashboard/services/validators.py

class DataSchemaValidator:
    """엑셀 데이터 스키마 검증"""

    STUDENT_REQUIRED_COLUMNS = [
        '학번', '이름', '단과대학', '학과', '과정구분', '학적상태'
    ]

    DEPARTMENT_KPI_REQUIRED_COLUMNS = [
        '단과대학', '학과', '평가년도', '졸업생취업률', '전임교원수'
    ]

    PUBLICATION_REQUIRED_COLUMNS = [
        '논문ID', '게재일자', '단과대학', '학과', '논문제목'
    ]

    RESEARCH_PROJECT_REQUIRED_COLUMNS = [
        '과제번호', '과제명', '연구책임자', '단과대학', '학과'
    ]

    @staticmethod
    def validate_columns(df, required_columns: List[str], sheet_name: str) -> None:
        """필수 컬럼 존재 여부 검증"""
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValidationError(
                f"{sheet_name} 시트: 필수 컬럼이 누락되었습니다: {', '.join(missing)}"
            )

    @staticmethod
    def validate_not_empty(df, sheet_name: str) -> None:
        """데이터가 비어있지 않은지 검증"""
        if df.empty:
            raise ValidationError(f"{sheet_name} 시트: 데이터가 없습니다.")
```

#### 2.4.2 Excel Import Service
```python
# apps/dashboard/services/excel_importer.py

import pandas as pd
from typing import Dict, List
from django.db import transaction

class ExcelImportService:
    """엑셀 파일 Import 비즈니스 로직"""

    def __init__(
        self,
        college_repo: CollegeRepository,
        department_repo: DepartmentRepository,
        student_repo: StudentRepository,
        kpi_repo: DepartmentKPIRepository,
        publication_repo: PublicationRepository,
        project_repo: ResearchProjectRepository,
        expense_repo: ProjectExpenseRepository
    ):
        self.college_repo = college_repo
        self.department_repo = department_repo
        self.student_repo = student_repo
        self.kpi_repo = kpi_repo
        self.publication_repo = publication_repo
        self.project_repo = project_repo
        self.expense_repo = expense_repo
        self.validator = DataSchemaValidator()

    @transaction.atomic
    def import_from_excel(self, file_path: str) -> Dict[str, int]:
        """
        엑셀 파일을 읽어 데이터베이스에 저장

        Returns:
            각 테이블별 삽입된 레코드 수
        """
        # 1. 엑셀 파일 읽기
        dataframes = self._read_excel_file(file_path)

        # 2. 데이터 검증
        self._validate_data(dataframes)

        # 3. 기존 데이터 삭제
        self._delete_existing_data()

        # 4. 단과대학 및 학과 추출 및 저장
        college_mapping, department_mapping = self._save_colleges_and_departments(dataframes)

        # 5. 각 테이블 데이터 저장
        result = {
            'students': self._save_students(dataframes['students'], department_mapping),
            'department_kpis': self._save_kpis(dataframes['kpis'], department_mapping),
            'publications': self._save_publications(dataframes['publications'], department_mapping),
            'projects': self._save_projects_and_expenses(dataframes['projects'], department_mapping)
        }

        return result

    def _read_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """엑셀 파일 읽기"""
        try:
            # 실제 구현: pd.read_excel() 사용
            # 여러 시트를 읽어 딕셔너리로 반환
            pass
        except Exception as e:
            raise ValidationError(f"엑셀 파일을 읽을 수 없습니다: {str(e)}")

    def _validate_data(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """모든 데이터프레임 검증"""
        self.validator.validate_columns(
            dataframes['students'],
            self.validator.STUDENT_REQUIRED_COLUMNS,
            'student_roster'
        )
        # ... 다른 시트도 검증

    def _delete_existing_data(self) -> None:
        """기존 데이터 삭제 (외래 키 순서 고려)"""
        self.expense_repo.delete_all()
        self.project_repo.delete_all()
        self.publication_repo.delete_all()
        self.kpi_repo.delete_all()
        self.student_repo.delete_all()
        self.department_repo.delete_all()
        self.college_repo.delete_all()

    def _save_colleges_and_departments(self, dataframes: Dict[str, pd.DataFrame]):
        """
        모든 데이터프레임에서 단과대학과 학과 추출 후 저장

        Returns:
            (college_mapping, department_mapping): ID 매핑 딕셔너리
        """
        # 모든 시트에서 '단과대학', '학과' 컬럼 추출
        # 중복 제거 후 저장
        # 이름 -> ID 매핑 딕셔너리 생성
        pass

    def _save_students(self, df: pd.DataFrame, dept_mapping: dict) -> int:
        """학생 데이터 저장"""
        students = []
        for _, row in df.iterrows():
            student = Student(
                student_id_number=row['학번'],
                name=row['이름'],
                department_id=dept_mapping[row['학과']],
                grade=row.get('학년'),
                program_level=row['과정구분'],
                status=row['학적상태'],
                gender=row.get('성별'),
                admission_year=row.get('입학년도'),
                advisor_name=row.get('지도교수'),
                email=row.get('이메일')
            )
            students.append(student)

        self.student_repo.bulk_create(students)
        return len(students)

    # _save_kpis, _save_publications, _save_projects_and_expenses 메소드 구현
```

**테스트 케이스:**
- 정상 파일 Import 성공
- 필수 컬럼 누락 시 ValidationError
- 빈 파일 처리
- 트랜잭션 롤백 (중간 실패 시)
- 대용량 데이터 처리 성능

**우선순위:** 높음 (P1)

**예상 소요 시간:** 6시간

---

### 2.5 Dashboard Summary Service (대시보드 데이터 집계)

**목적:** 메인 대시보드에 표시할 데이터를 집계하고 차트 형식으로 가공

**참조 유스케이스:** UC-003 (메인 대시보드 조회)

**구현 범위:**

```python
# apps/dashboard/services/summary_generator.py

class DashboardSummaryService:
    """대시보드 요약 데이터 생성"""

    def __init__(
        self,
        student_repo: StudentRepository,
        publication_repo: PublicationRepository,
        kpi_repo: DepartmentKPIRepository,
        expense_repo: ProjectExpenseRepository
    ):
        self.student_repo = student_repo
        self.publication_repo = publication_repo
        self.kpi_repo = kpi_repo
        self.expense_repo = expense_repo

    def generate_dashboard_summary(self) -> dict:
        """
        대시보드 전체 데이터 생성

        Returns:
            {
                'is_empty': bool,
                'performance_by_department': list,
                'publications_by_year': list,
                'students_by_status': list,
                'budget_execution': dict
            }
        """
        # 데이터 존재 여부 확인
        if self._is_data_empty():
            return {'is_empty': True}

        return {
            'is_empty': False,
            'performance_by_department': self._get_performance_by_department(),
            'publications_by_year': self._get_publications_by_year(),
            'students_by_status': self._get_students_by_status(),
            'budget_execution': self._get_budget_execution()
        }

    def _is_data_empty(self) -> bool:
        """데이터베이스에 데이터가 있는지 확인"""
        return (
            self.student_repo.get_all() == [] and
            self.publication_repo.get_all() == []
        )

    def _get_performance_by_department(self) -> List[dict]:
        """학과별 종합 실적 (막대 그래프용)"""
        # 학과별 논문 수, 과제 수, 학생 수 집계
        pass

    def _get_publications_by_year(self) -> List[dict]:
        """연도별 논문 수 추이 (라인 차트용)"""
        return self.publication_repo.count_by_year()

    def _get_students_by_status(self) -> List[dict]:
        """학적 상태별 학생 수 (파이 차트용)"""
        status_counts = self.student_repo.count_by_status()
        return [
            {'status': status, 'count': count}
            for status, count in status_counts.items()
        ]

    def _get_budget_execution(self) -> dict:
        """예산 집행률 (게이지 차트용)"""
        execution_rate = self.expense_repo.calculate_execution_rate()
        # ... 총 예산, 집행 금액 등 계산
        return {
            'total_budget': 0,
            'executed_amount': 0,
            'execution_rate': execution_rate
        }
```

**테스트 케이스:**
- 데이터 없을 때 is_empty=True 반환
- 각 차트 데이터 형식 검증
- 집계 로직 정확성 검증

**우선순위:** 높음 (P1)

**예상 소요 시간:** 4시간

---

### 2.6 API Serializers (데이터 직렬화)

**목적:** Django 모델을 JSON으로 변환하는 Serializer 정의

**구현 범위:**

```python
# apps/dashboard/serializers.py

from rest_framework import serializers

class DashboardSummarySerializer(serializers.Serializer):
    """대시보드 요약 응답 Serializer"""
    is_empty = serializers.BooleanField()
    performance_by_department = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    publications_by_year = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    students_by_status = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    budget_execution = serializers.DictField(required=False)

class FileUploadSerializer(serializers.Serializer):
    """파일 업로드 요청 Serializer"""
    file = serializers.FileField()

    def validate_file(self, value):
        """파일 확장자 검증"""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError(
                "엑셀 파일(.xlsx, .xls)만 업로드할 수 있습니다."
            )
        return value
```

**우선순위:** 중간 (P2)

**예상 소요 시간:** 2시간

---

## 3. 프론트엔드 공통 모듈

### 3.1 API Client (HTTP 통신 레이어)

**목적:** 백엔드 API와의 모든 HTTP 통신을 중앙 관리

**구현 범위:**

#### 3.1.1 Axios 인스턴스 설정
```javascript
// src/api/index.js

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: JWT 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로 리다이렉트
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 3.1.2 API 함수 정의
```javascript
// src/api/authAPI.js

import apiClient from './index';

export const authAPI = {
  /**
   * 로그인
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{access_token: string, user: object}>}
   */
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login/', { email, password });
    return response.data;
  },

  /**
   * 로그아웃
   */
  logout: async () => {
    await apiClient.post('/auth/logout/');
    localStorage.removeItem('access_token');
  },

  /**
   * 사용자 프로필 조회
   */
  getProfile: async () => {
    const response = await apiClient.get('/auth/profile/');
    return response.data;
  }
};
```

```javascript
// src/api/dashboardAPI.js

import apiClient from './index';

export const dashboardAPI = {
  /**
   * 대시보드 요약 데이터 조회
   */
  getSummary: async () => {
    const response = await apiClient.get('/dashboard/summary/');
    return response.data;
  }
};
```

```javascript
// src/api/dataUploadAPI.js

import apiClient from './index';

export const dataUploadAPI = {
  /**
   * 엑셀 파일 업로드
   * @param {File} file
   */
  uploadExcel: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/data-upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
};
```

**테스트 케이스:**
- 토큰 자동 추가 확인
- 401 응답 시 자동 로그아웃
- 네트워크 에러 처리
- 타임아웃 처리

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 3시간

---

### 3.2 전역 상태 관리 (State Management)

**목적:** 사용자 인증 정보 및 전역 상태 관리

**구현 범위:**

```javascript
// src/store/authStore.js

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // 상태
      user: null,
      isAuthenticated: false,

      // 액션
      setUser: (user) => set({ user, isAuthenticated: true }),

      logout: () => set({ user: null, isAuthenticated: false }),

      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin';
      }
    }),
    {
      name: 'auth-storage',
      getStorage: () => localStorage
    }
  )
);

export default useAuthStore;
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 1시간

---

### 3.3 공통 UI 컴포넌트

**목적:** 재사용 가능한 UI 컴포넌트 라이브러리 구축

**구현 범위:**

#### 3.3.1 Button 컴포넌트
```jsx
// src/components/common/Button.jsx

const Button = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  loading = false,
  type = 'button',
  ...props
}) => {
  const baseStyles = 'px-4 py-2 rounded font-medium transition-colors';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variants[variant]}`}
      {...props}
    >
      {loading ? '처리 중...' : children}
    </button>
  );
};

export default Button;
```

#### 3.3.2 Input 컴포넌트
```jsx
// src/components/common/Input.jsx

const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  error,
  placeholder,
  required = false,
  ...props
}) => {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full px-3 py-2 border rounded ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        {...props}
      />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
};

export default Input;
```

#### 3.3.3 LoadingSpinner 컴포넌트
```jsx
// src/components/common/LoadingSpinner.jsx

const LoadingSpinner = ({ size = 'medium' }) => {
  const sizes = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex justify-center items-center">
      <div className={`${sizes[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}></div>
    </div>
  );
};

export default LoadingSpinner;
```

#### 3.3.4 ErrorMessage 컴포넌트
```jsx
// src/components/common/ErrorMessage.jsx

const ErrorMessage = ({ message, onRetry }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded p-4 text-center">
      <p className="text-red-700 mb-2">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-red-600 underline hover:text-red-800"
        >
          다시 시도
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
```

#### 3.3.5 EmptyState 컴포넌트
```jsx
// src/components/common/EmptyState.jsx

const EmptyState = ({ message, icon }) => {
  return (
    <div className="text-center py-12">
      {icon && <div className="text-4xl mb-4">{icon}</div>}
      <p className="text-gray-500">{message}</p>
    </div>
  );
};

export default EmptyState;
```

**우선순위:** 높음 (P1)

**예상 소요 시간:** 4시간

---

### 3.4 레이아웃 컴포넌트

**목적:** 모든 페이지에서 사용되는 공통 레이아웃

**구현 범위:**

#### 3.4.1 Header (GNB)
```jsx
// src/components/layout/Header.jsx

import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import { authAPI } from '../../api/authAPI';

const Header = () => {
  const { user, isAdmin, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      logout();
      navigate('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  return (
    <header className="bg-white shadow">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/dashboard" className="text-xl font-bold">
          대학 데이터 대시보드
        </Link>

        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="hover:text-blue-600">
            대시보드
          </Link>

          {isAdmin() && (
            <Link to="/upload" className="hover:text-blue-600">
              데이터 관리
            </Link>
          )}

          <div className="flex items-center gap-2">
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
```

#### 3.4.2 MainLayout
```jsx
// src/components/layout/MainLayout.jsx

import Header from './Header';

const MainLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
```

**우선순위:** 높음 (P1)

**예상 소요 시간:** 2시간

---

### 3.5 커스텀 훅 (Custom Hooks)

**목적:** 재사용 가능한 로직을 훅으로 추상화

**구현 범위:**

```javascript
// src/hooks/useApi.js

import { useState, useEffect } from 'react';

/**
 * API 호출을 위한 커스텀 훅
 * @param {Function} apiFunc - API 호출 함수
 * @param {boolean} immediate - 컴포넌트 마운트 시 즉시 호출 여부
 */
const useApi = (apiFunc, immediate = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (...params) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiFunc(...params);
      setData(result);
      return result;
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, []);

  return { data, loading, error, execute };
};

export default useApi;
```

```javascript
// src/hooks/useAuth.js

import useAuthStore from '../store/authStore';
import { authAPI } from '../api/authAPI';
import { useNavigate } from 'react-router-dom';

const useAuth = () => {
  const { user, isAuthenticated, setUser, logout } = useAuthStore();
  const navigate = useNavigate();

  const login = async (email, password) => {
    try {
      const { access_token, user: userData } = await authAPI.login(email, password);
      localStorage.setItem('access_token', access_token);
      setUser(userData);
      navigate('/dashboard');
    } catch (error) {
      throw error;
    }
  };

  const handleLogout = async () => {
    await authAPI.logout();
    logout();
    navigate('/login');
  };

  return { user, isAuthenticated, login, logout: handleLogout };
};

export default useAuth;
```

**우선순위:** 중간 (P2)

**예상 소요 시간:** 2시간

---

### 3.6 라우팅 및 인증 가드

**목적:** 페이지 라우팅 및 인증 기반 접근 제어

**구현 범위:**

```jsx
// src/components/auth/ProtectedRoute.jsx

import { Navigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isAdmin } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

```jsx
// src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/upload"
          element={
            <ProtectedRoute adminOnly>
              <UploadPage />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 2시간

---

## 4. 테스트 환경 설정

### 4.1 백엔드 테스트 환경

**목적:** TDD 개발을 위한 백엔드 테스트 환경 구축

**참조 문서:** `/docs/rules/tdd.md`

**구현 범위:**

#### 4.1.1 pytest 설정
```python
# backend/pytest.ini

[pytest]
DJANGO_SETTINGS_MODULE = dashboard_project.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts =
    --tb=short
    --strict-markers
    --disable-warnings
    -v
```

#### 4.1.2 conftest.py (공통 Fixture)
```python
# backend/conftest.py

import pytest
from django.contrib.auth import get_user_model
from apps.users.models import Profile, UserRole
from apps.dashboard.models import College, Department

User = get_user_model()

@pytest.fixture
def sample_college():
    """테스트용 단과대학"""
    return College.objects.create(name='공과대학')

@pytest.fixture
def sample_department(sample_college):
    """테스트용 학과"""
    return Department.objects.create(
        college=sample_college,
        name='컴퓨터공학과'
    )

@pytest.fixture
def admin_user():
    """테스트용 관리자"""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123'
    )
    Profile.objects.create(id=user.id, role=UserRole.ADMIN)
    return user

@pytest.fixture
def general_user():
    """테스트용 일반 사용자"""
    user = User.objects.create_user(
        username='user',
        email='user@test.com',
        password='testpass123'
    )
    Profile.objects.create(id=user.id, role=UserRole.GENERAL)
    return user

@pytest.fixture
def mock_student_repo():
    """Mock StudentRepository"""
    from unittest.mock import MagicMock
    return MagicMock()
```

#### 4.1.3 테스트 커버리지 설정
```ini
# backend/.coveragerc

[run]
source = apps/
omit =
    */migrations/*
    */tests/*
    */test_*.py
    */__init__.py

[report]
precision = 2
show_missing = True
skip_covered = False
```

**실행 명령어:**
```bash
# 모든 테스트 실행
pytest

# 특정 앱 테스트
pytest apps/dashboard/tests/

# 커버리지 포함
pytest --cov=apps --cov-report=html
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 3시간

---

### 4.2 프론트엔드 테스트 환경

**목적:** 프론트엔드 컴포넌트 및 로직 테스트 환경

**구현 범위:**

#### 4.2.1 Vitest 설정
```javascript
// frontend/vitest.config.js

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'c8',
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
      ],
    },
  },
});
```

#### 4.2.2 테스트 설정 파일
```javascript
// frontend/src/test/setup.js

import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

#### 4.2.3 Mock API 헬퍼
```javascript
// frontend/src/test/mockApi.js

import { vi } from 'vitest';

export const mockApiResponse = (data, delay = 100) => {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ data }), delay);
  });
};

export const mockApiError = (message, status = 500, delay = 100) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject({
      response: { status, data: { message } }
    }), delay);
  });
};
```

**실행 명령어:**
```bash
# 모든 테스트 실행
npm run test

# Watch 모드
npm run test:watch

# 커버리지
npm run test:coverage
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 2시간

---

## 5. 개발 도구 및 코드 품질 관리

### 5.1 코드 포맷터 및 린터

**목적:** 일관된 코드 스타일 유지

**구현 범위:**

#### 5.1.1 백엔드 (Python)
```ini
# backend/.flake8

[flake8]
max-line-length = 100
exclude =
    .git,
    __pycache__,
    migrations,
    venv
ignore = E203, W503
```

```toml
# backend/pyproject.toml

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
```

#### 5.1.2 프론트엔드 (JavaScript)
```json
// frontend/.eslintrc.json

{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "react/prop-types": "off",
    "no-unused-vars": "warn"
  }
}
```

```json
// frontend/.prettierrc

{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

**우선순위:** 중간 (P2)

**예상 소요 시간:** 1시간

---

### 5.2 Git Pre-commit Hooks

**목적:** 커밋 전 자동 코드 품질 검사

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

**우선순위:** 낮음 (P3)

**예상 소요 시간:** 1시간

---

## 6. 데이터베이스 마이그레이션

### 6.1 초기 마이그레이션 생성

**목적:** database.md의 스키마를 Django 마이그레이션으로 생성

**작업 내용:**
1. 모든 모델 정의 완료 후 마이그레이션 생성
2. 인덱스 추가 마이그레이션 생성
3. 초기 데이터(Seed Data) 마이그레이션 생성 (선택)

**명령어:**
```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 데이터베이스 적용
python manage.py migrate

# 초기 관리자 계정 생성
python manage.py createsuperuser
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 1시간

---

## 7. 환경 변수 및 설정 관리

### 7.1 백엔드 환경 변수

```bash
# backend/.env.example

# Django 설정
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# 데이터베이스 (Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS 설정
CORS_ALLOWED_ORIGINS=http://localhost:5173

# 파일 업로드 설정
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### 7.2 프론트엔드 환경 변수

```bash
# frontend/.env.example

# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Supabase (클라이언트 SDK용)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**우선순위:** 최우선 (P0)

**예상 소요 시간:** 1시간

---

## 8. 구현 우선순위 및 작업 순서

### Phase 0: 초기 설정 (총 8시간)
1. 백엔드 프로젝트 초기화 (2h)
2. 프론트엔드 프로젝트 초기화 (2h)
3. 환경 변수 설정 (1h)
4. 데이터베이스 연결 확인 (1h)
5. Git 저장소 설정 및 .gitignore (0.5h)
6. README.md 작성 (0.5h)
7. 개발 환경 실행 검증 (1h)

### Phase 1: 핵심 인프라 (총 15시간)
1. 데이터베이스 모델 정의 (3h)
2. 마이그레이션 생성 및 적용 (1h)
3. 인증/인가 시스템 (4h)
4. Repository 레이어 구현 (4h)
5. 테스트 환경 설정 (백엔드 3h)

### Phase 2: 비즈니스 로직 (총 14시간)
1. Excel Import Service (6h)
2. Dashboard Summary Service (4h)
3. API Serializers (2h)
4. 프론트엔드 테스트 환경 (2h)

### Phase 3: 프론트엔드 공통 (총 14시간)
1. API Client (3h)
2. 전역 상태 관리 (1h)
3. 라우팅 및 인증 가드 (2h)
4. 공통 UI 컴포넌트 (4h)
5. 레이아웃 컴포넌트 (2h)
6. 커스텀 훅 (2h)

### Phase 4: 코드 품질 도구 (총 2시간)
1. 린터 및 포맷터 설정 (1h)
2. Pre-commit hooks (1h)

**총 예상 소요 시간: 53시간 (약 7일)**

---

## 9. 검증 체크리스트

공통 모듈 구현 완료 후 다음 항목들을 검증해야 합니다:

### 백엔드
- [ ] Django 프로젝트가 정상적으로 실행되는가?
- [ ] Supabase PostgreSQL에 연결되는가?
- [ ] 모든 데이터베이스 모델이 마이그레이션되었는가?
- [ ] 인증 미들웨어가 JWT 토큰을 올바르게 검증하는가?
- [ ] Repository의 모든 메소드에 단위 테스트가 작성되었는가?
- [ ] ExcelImportService의 주요 시나리오에 테스트가 작성되었는가?
- [ ] pytest로 모든 테스트가 통과하는가?

### 프론트엔드
- [ ] Vite 개발 서버가 정상적으로 실행되는가?
- [ ] API Client가 백엔드와 통신하는가?
- [ ] 인증 토큰이 자동으로 헤더에 추가되는가?
- [ ] 401 응답 시 자동 로그아웃이 동작하는가?
- [ ] 전역 상태 관리가 정상 작동하는가?
- [ ] ProtectedRoute가 인증되지 않은 사용자를 차단하는가?
- [ ] 모든 공통 컴포넌트가 스토리북 또는 테스트로 검증되었는가?

### 통합
- [ ] 로컬 환경에서 백엔드와 프론트엔드가 동시에 실행되는가?
- [ ] CORS 설정이 올바르게 되어 있는가?
- [ ] 환경 변수가 올바르게 로드되는가?

---

## 10. 리스크 관리

### 10.1 기술적 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| Supabase Auth 통합 복잡도 | 중 | Supabase 공식 문서 및 샘플 코드 사전 검토 |
| 엑셀 파일 파싱 오류 | 중 | 다양한 엣지 케이스에 대한 단위 테스트 작성 |
| 데이터베이스 마이그레이션 실패 | 높 | 로컬 환경에서 충분한 테스트 후 적용 |
| 프론트엔드 라이브러리 호환성 | 낮 | 최신 안정 버전 사용, package-lock.json 커밋 |

### 10.2 일정 리스크

| 리스크 | 영향도 | 완화 전략 |
|--------|--------|-----------|
| 테스트 작성 시간 부족 | 중 | 핵심 로직에만 집중, E2E는 이후 단계로 이연 |
| 기술 학습 곡선 | 중 | 팀원간 페어 프로그래밍, 코드 리뷰 |

---

## 11. 다음 단계

공통 모듈 구축 완료 후 다음 단계로 진행합니다:

1. **페이지 단위 개발 (병렬 작업 가능)**
   - 로그인 페이지 (UC-001)
   - 데이터 업로드 페이지 (UC-002)
   - 메인 대시보드 페이지 (UC-003)

2. **통합 테스트 및 E2E 테스트**

3. **배포 준비 (Railway)**

---

## 참고 문서

- `/docs/PRD.md` - 제품 요구사항 정의서
- `/docs/userflow.md` - 사용자 플로우
- `/docs/database.md` - 데이터베이스 스키마
- `/docs/structure.md` - 아키텍처 설계
- `/docs/techstack.md` - 기술 스택 선정 배경
- `/docs/rules/tdd.md` - TDD 가이드라인
- `/docs/usecases/01-login/spec.md` - 로그인 유스케이스
- `/docs/usecases/02-excel-upload/spec.md` - 엑셀 업로드 유스케이스
- `/docs/usecases/03-main-dashboard-view/spec.md` - 대시보드 조회 유스케이스

---

**작성 완료일:** 2025-11-13
**최종 검토자:** Development Team
**승인일:** [TBD]
