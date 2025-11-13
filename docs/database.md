### 1. 데이터플로우 (Data Flow)

1.  **인증 플로우 (Authentication Flow)**
    *   (기존과 동일) 사용자는 ID/PW를 통해 `Supabase Auth`로 인증하고, 시스템은 `profiles` 테이블의 `role`을 기반으로 권한을 확인합니다.

2.  **데이터 갱신 플로우 (Data Update Flow - 관리자)**
    *   `관리자` → **(데이터 파일(들) 업로드)** → `백엔드 API`
    *   `백엔드 API` → **(데이터베이스 트랜잭션 시작)**
    *   `백엔드 API` → **(1. 기존 데이터 전체 삭제)**
        *   `TRUNCATE` 명령어를 사용하여 `department_kpis`, `publications`, `project_expenses`, `research_projects`, `students`, `departments`, `colleges` 테이블을 순서대로 초기화합니다. (외래 키 제약조건 순서 준수)
    *   `백엔드 API` → **(2. 신규 데이터 파싱 및 저장)**
        *   **(Colleges, Departments)**: `student_roster.csv` 등 모든 파일에 있는 '단과대학'과 '학과' 정보를 취합하여 중복을 제거한 후, `colleges`와 `departments` 테이블에 먼저 `INSERT` 합니다. 이는 데이터 무결성을 위한 선행 작업입니다.
        *   **(Students)**: `student_roster.csv`를 읽어 `students` 테이블에 `INSERT` 합니다.
        *   **(Department KPIs)**: `department_kpi.csv`를 읽어 `department_kpis` 테이블에 `INSERT` 합니다.
        *   **(Research Projects, Project Expenses)**: `research_project_data.csv`를 읽어 과제번호(`과제번호`)를 기준으로 `research_projects` (과제 정보)와 `project_expenses` (개별 집행 내역) 테이블에 나누어 `INSERT` 합니다.
        *   **(Publications)**: `publication_list.csv`를 읽어 `publications` 테이블에 `INSERT` 합니다.
    *   `백엔드 API` → **(처리 중 오류 발생 시 트랜잭션 롤백)** → `관리자`에게 오류 메시지 응답
    *   `백엔드 API` → **(모든 데이터 저장 성공 시 트랜잭션 커밋)** → `관리자`에게 "성공" 응답
    *   **핵심 변경점:** 데이터 처리를 **하나의 트랜잭션**으로 묶어, 중간에 하나라도 실패하면 모든 변경사항이 취소(Rollback)되도록 하여 데이터의 정합성을 보장합니다.

3.  **데이터 조회 플로우 (Data Read Flow - 모든 사용자)**
    *   (기존과 유사) 사용자가 대시보드에 접속하면, 백엔드는 **여러 테이블을 `JOIN`하여** 시각화에 필요한 데이터를 동적으로 집계하고 가공하여 JSON 형태로 제공합니다. 예를 들어 '학과별 논문 수'는 `departments`와 `publications` 테이블을 조인하여 계산합니다.

---

### 2. 데이터베이스 스키마 (Database Schema) - 수정 제안

데이터를 정규화하여 중복을 최소화하고 관계를 명확하게 정의합니다. `단과대학`, `학과`와 같이 중복되는 정보는 별도의 테이블로 분리합니다.

#### **Core Entities (핵심 독립 테이블)**
*   `profiles`: 사용자 역할 관리 (기존과 동일)
*   `colleges`: 단과대학 정보
*   `departments`: 학과 정보 (단과대학에 소속)

#### **Dependent Data (핵심 데이터 테이블)**
*   `students`: 학생 명단
*   `department_kpis`: 학과별 핵심 성과 지표
*   `publications`: 논문 목록
*   `research_projects`: 연구 과제 정보
*   `project_expenses`: 연구 과제별 예산 집행 내역

---

### 3. 최종 제안 (Migration SQL 포함)

새롭게 설계된 데이터플로우와 정규화된 스키마를 데이터베이스에 즉시 반영할 수 있는 최종 SQL 마이그레이션 스크립트입니다.

```sql
-- 대학교 데이터 시각화 대시보드 MVP v2 마이그레이션 스크립트
-- 최종 작성일: 2025년 11월 13일
-- 변경사항: 제공된 CSV 파일 구조를 반영하여 스키마 정규화
-- 작성자: CTO

-- 기존 테이블이 존재할 경우를 대비하여 초기화 (개발 환경용)
DROP TABLE IF EXISTS public.project_expenses, public.research_projects, public.publications, public.department_kpis, public.students, public.departments, public.colleges, public.profiles;
DROP TYPE IF EXISTS public.user_role, public.academic_program, public.academic_status, public.project_status;

-- ==== 1. ENUM 타입 정의 ====
-- 반복적으로 사용되는 특정 문자열 값들을 ENUM으로 정의하여 데이터 일관성을 강화합니다.
CREATE TYPE public.user_role AS ENUM ('admin', 'general');
CREATE TYPE public.academic_program AS ENUM ('학사', '석사', '박사');
CREATE TYPE public.academic_status AS ENUM ('재학', '휴학', '졸업');
CREATE TYPE public.project_status AS ENUM ('처리중', '집행완료', '반려');


-- ==== 2. 사용자 프로필 테이블 (변경 없음) ====
CREATE TABLE public.profiles (
    id uuid NOT NULL PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role public.user_role NOT NULL DEFAULT 'general',
    username text,
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.profiles IS '사용자 역할 등 애플리케이션 관련 프로필 정보';


-- ==== 3. 핵심 엔티티 테이블 (단과대학, 학과) ====
CREATE TABLE public.colleges (
    id bigserial PRIMARY KEY,
    name varchar(255) NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.colleges IS '단과대학 정보 마스터 테이블';

CREATE TABLE public.departments (
    id bigserial PRIMARY KEY,
    college_id bigint NOT NULL REFERENCES public.colleges(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (college_id, name) -- 단과대학 내에서 학과 이름은 유일해야 함
);
COMMENT ON TABLE public.departments IS '학과 정보 마스터 테이블';


-- ==== 4. 데이터 테이블들 ====

-- 4.1. 학생 명단 (student_roster.csv)
CREATE TABLE public.students (
    id bigserial PRIMARY KEY,
    student_id_number varchar(50) NOT NULL UNIQUE,
    name varchar(100) NOT NULL,
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE RESTRICT,
    grade smallint, -- 학년
    program_level public.academic_program NOT NULL, -- 과정구분 (학사, 석사)
    status public.academic_status NOT NULL, -- 학적상태
    gender char(1),
    admission_year integer,
    advisor_name varchar(100),
    email varchar(255) UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.students IS '학생 명단 데이터 (student_roster.csv)';

-- 4.2. 학과 KPI (department_kpi.csv)
CREATE TABLE public.department_kpis (
    id bigserial PRIMARY KEY,
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE CASCADE,
    evaluation_year integer NOT NULL,
    employment_rate numeric(5, 2), -- 졸업생 취업률
    full_time_faculty_count integer, -- 전임교원 수
    visiting_faculty_count integer, -- 초빙교원 수
    tech_transfer_income numeric(10, 2), -- 연간 기술이전 수입액 (억원)
    international_conferences_count integer, -- 국제학술대회 개최 횟수
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (department_id, evaluation_year)
);
COMMENT ON TABLE public.department_kpis IS '학과별 연간 KPI 데이터 (department_kpi.csv)';

-- 4.3. 논문 목록 (publication_list.csv)
CREATE TABLE public.publications (
    id bigserial PRIMARY KEY,
    publication_id_str varchar(100) UNIQUE, -- 논문ID (e.g., PUB-23-001)
    publication_date date NOT NULL,
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE RESTRICT,
    title text NOT NULL,
    primary_author varchar(100),
    contributing_authors text,
    journal_name text,
    journal_rank varchar(50),
    impact_factor numeric(6, 3),
    is_project_linked boolean,
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.publications IS '논문 게재 목록 데이터 (publication_list.csv)';

-- 4.4. 연구 과제 (research_project_data.csv - Part 1)
CREATE TABLE public.research_projects (
    id bigserial PRIMARY KEY,
    project_number varchar(100) NOT NULL UNIQUE, -- 과제번호
    name text NOT NULL,
    principal_investigator varchar(100), -- 연구책임자
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE RESTRICT,
    funding_agency varchar(255), -- 지원기관
    total_funding_amount bigint, -- 총연구비
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.research_projects IS '연구 과제 마스터 정보 (research_project_data.csv)';

-- 4.5. 연구 과제 집행 내역 (research_project_data.csv - Part 2)
CREATE TABLE public.project_expenses (
    id bigserial PRIMARY KEY,
    execution_id varchar(100) NOT NULL UNIQUE, -- 집행ID
    project_id bigint NOT NULL REFERENCES public.research_projects(id) ON DELETE CASCADE,
    execution_date date NOT NULL,
    item varchar(255) NOT NULL, -- 집행항목
    amount bigint NOT NULL, -- 집행금액
    status public.project_status NOT NULL,
    notes text,
    created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE public.project_expenses IS '연구 과제별 예산 집행 내역 (research_project_data.csv)';


-- ==== 5. 조회 성능 향상을 위한 인덱스 생성 ====
CREATE INDEX idx_departments_college_id ON public.departments (college_id);
CREATE INDEX idx_students_department_id ON public.students (department_id);
CREATE INDEX idx_department_kpis_dept_year ON public.department_kpis (department_id, evaluation_year);
CREATE INDEX idx_publications_department_id ON public.publications (department_id);
CREATE INDEX idx_research_projects_department_id ON public.research_projects (department_id);
CREATE INDEX idx_project_expenses_project_id ON public.project_expenses (project_id);
```