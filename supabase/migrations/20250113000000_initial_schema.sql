-- =============================================================================
-- 대학교 데이터 시각화 대시보드 - 초기 스키마 마이그레이션
-- =============================================================================
-- 작성일: 2025-01-13
-- 설명: 대학 성과 데이터 시각화를 위한 전체 데이터베이스 스키마 생성
-- =============================================================================

-- 기존 테이블 삭제 (개발 환경 초기화용)
DROP TABLE IF EXISTS public.project_expenses CASCADE;
DROP TABLE IF EXISTS public.research_projects CASCADE;
DROP TABLE IF EXISTS public.publications CASCADE;
DROP TABLE IF EXISTS public.department_kpis CASCADE;
DROP TABLE IF EXISTS public.students CASCADE;
DROP TABLE IF EXISTS public.departments CASCADE;
DROP TABLE IF EXISTS public.colleges CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- 기존 ENUM 타입 삭제
DROP TYPE IF EXISTS public.user_role CASCADE;
DROP TYPE IF EXISTS public.academic_program CASCADE;
DROP TYPE IF EXISTS public.academic_status CASCADE;
DROP TYPE IF EXISTS public.project_status CASCADE;


-- =============================================================================
-- ENUM 타입 정의
-- =============================================================================

-- 사용자 역할
CREATE TYPE public.user_role AS ENUM ('admin', 'general');
COMMENT ON TYPE public.user_role IS '사용자 역할: admin(관리자), general(일반 사용자)';

-- 학위 과정
CREATE TYPE public.academic_program AS ENUM ('학사', '석사', '박사');
COMMENT ON TYPE public.academic_program IS '학위 과정 구분';

-- 학적 상태
CREATE TYPE public.academic_status AS ENUM ('재학', '휴학', '졸업');
COMMENT ON TYPE public.academic_status IS '학생 학적 상태';

-- 프로젝트 집행 상태
CREATE TYPE public.project_status AS ENUM ('처리중', '집행완료', '반려');
COMMENT ON TYPE public.project_status IS '연구 과제 예산 집행 상태';


-- =============================================================================
-- 1. 사용자 프로필 테이블
-- =============================================================================

CREATE TABLE public.profiles (
    id uuid NOT NULL PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role public.user_role NOT NULL DEFAULT 'general',
    username text,
    email varchar(254),
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.profiles IS '사용자 프로필 - Supabase Auth와 연동';
COMMENT ON COLUMN public.profiles.id IS 'Supabase Auth 사용자 UUID';
COMMENT ON COLUMN public.profiles.role IS '사용자 역할 (admin/general)';
COMMENT ON COLUMN public.profiles.username IS '사용자 이름';
COMMENT ON COLUMN public.profiles.email IS '사용자 이메일';


-- =============================================================================
-- 2. 핵심 엔티티 테이블 (단과대학, 학과)
-- =============================================================================

CREATE TABLE public.colleges (
    id bigserial PRIMARY KEY,
    name varchar(255) NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.colleges IS '단과대학 정보';
COMMENT ON COLUMN public.colleges.name IS '단과대학 이름 (중복 불가)';

CREATE TABLE public.departments (
    id bigserial PRIMARY KEY,
    college_id bigint NOT NULL REFERENCES public.colleges(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT unique_department_per_college UNIQUE (college_id, name)
);

COMMENT ON TABLE public.departments IS '학과 정보';
COMMENT ON COLUMN public.departments.college_id IS '소속 단과대학';
COMMENT ON COLUMN public.departments.name IS '학과 이름 (단과대학 내 중복 불가)';


-- =============================================================================
-- 3. 학생 명단 테이블
-- =============================================================================

CREATE TABLE public.students (
    id bigserial PRIMARY KEY,
    student_id_number varchar(50) NOT NULL UNIQUE,
    name varchar(100) NOT NULL,
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE RESTRICT,
    grade smallint,
    program_level public.academic_program NOT NULL,
    status public.academic_status NOT NULL,
    gender char(1),
    admission_year integer,
    advisor_name varchar(100),
    email varchar(255) UNIQUE,
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.students IS '학생 명단 데이터 (student_roster.csv)';
COMMENT ON COLUMN public.students.student_id_number IS '학번 (중복 불가)';
COMMENT ON COLUMN public.students.department_id IS '소속 학과';
COMMENT ON COLUMN public.students.grade IS '학년';
COMMENT ON COLUMN public.students.program_level IS '학위 과정 (학사/석사/박사)';
COMMENT ON COLUMN public.students.status IS '학적 상태 (재학/휴학/졸업)';


-- =============================================================================
-- 4. 학과 KPI 테이블
-- =============================================================================

CREATE TABLE public.department_kpis (
    id bigserial PRIMARY KEY,
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE CASCADE,
    evaluation_year integer NOT NULL,
    employment_rate numeric(5, 2),
    full_time_faculty_count integer,
    visiting_faculty_count integer,
    tech_transfer_income numeric(10, 2),
    international_conferences_count integer,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT unique_department_kpi_per_year UNIQUE (department_id, evaluation_year)
);

COMMENT ON TABLE public.department_kpis IS '학과별 연간 핵심 성과 지표 (department_kpi.csv)';
COMMENT ON COLUMN public.department_kpis.evaluation_year IS '평가 연도';
COMMENT ON COLUMN public.department_kpis.employment_rate IS '졸업생 취업률 (%)';
COMMENT ON COLUMN public.department_kpis.full_time_faculty_count IS '전임교원 수';
COMMENT ON COLUMN public.department_kpis.visiting_faculty_count IS '초빙교원 수';
COMMENT ON COLUMN public.department_kpis.tech_transfer_income IS '기술이전 수입액 (억원)';
COMMENT ON COLUMN public.department_kpis.international_conferences_count IS '국제학술대회 개최 횟수';


-- =============================================================================
-- 5. 논문 목록 테이블
-- =============================================================================

CREATE TABLE public.publications (
    id bigserial PRIMARY KEY,
    publication_id_str varchar(100) UNIQUE,
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

COMMENT ON TABLE public.publications IS '논문 게재 목록 (publication_list.csv)';
COMMENT ON COLUMN public.publications.publication_id_str IS '논문 ID (예: PUB-23-001)';
COMMENT ON COLUMN public.publications.publication_date IS '게재일';
COMMENT ON COLUMN public.publications.department_id IS '소속 학과';
COMMENT ON COLUMN public.publications.journal_rank IS '학술지 등급 (SCI, SCIE 등)';
COMMENT ON COLUMN public.publications.impact_factor IS '임팩트 팩터';
COMMENT ON COLUMN public.publications.is_project_linked IS '과제 연계 여부';


-- =============================================================================
-- 6. 연구 과제 테이블
-- =============================================================================

CREATE TABLE public.research_projects (
    id bigserial PRIMARY KEY,
    project_number varchar(100) NOT NULL UNIQUE,
    name text NOT NULL,
    principal_investigator varchar(100),
    department_id bigint NOT NULL REFERENCES public.departments(id) ON DELETE RESTRICT,
    funding_agency varchar(255),
    total_funding_amount bigint,
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.research_projects IS '연구 과제 정보 (research_project_data.csv)';
COMMENT ON COLUMN public.research_projects.project_number IS '과제번호 (중복 불가)';
COMMENT ON COLUMN public.research_projects.principal_investigator IS '연구책임자';
COMMENT ON COLUMN public.research_projects.funding_agency IS '지원기관';
COMMENT ON COLUMN public.research_projects.total_funding_amount IS '총 연구비 (원)';


-- =============================================================================
-- 7. 연구 과제 집행 내역 테이블
-- =============================================================================

CREATE TABLE public.project_expenses (
    id bigserial PRIMARY KEY,
    execution_id varchar(100) NOT NULL UNIQUE,
    project_id bigint NOT NULL REFERENCES public.research_projects(id) ON DELETE CASCADE,
    execution_date date NOT NULL,
    item varchar(255) NOT NULL,
    amount bigint NOT NULL,
    status public.project_status NOT NULL,
    notes text,
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.project_expenses IS '연구 과제 예산 집행 내역 (research_project_data.csv)';
COMMENT ON COLUMN public.project_expenses.execution_id IS '집행 ID (중복 불가)';
COMMENT ON COLUMN public.project_expenses.project_id IS '소속 연구 과제';
COMMENT ON COLUMN public.project_expenses.execution_date IS '집행일';
COMMENT ON COLUMN public.project_expenses.item IS '집행 항목';
COMMENT ON COLUMN public.project_expenses.amount IS '집행 금액 (원)';
COMMENT ON COLUMN public.project_expenses.status IS '집행 상태 (처리중/집행완료/반려)';


-- =============================================================================
-- 8. 성능 향상을 위한 인덱스 생성
-- =============================================================================

-- 학과별 조회 최적화
CREATE INDEX idx_departments_college_id ON public.departments (college_id);

-- 학생 조회 최적화
CREATE INDEX idx_students_department_id ON public.students (department_id);
CREATE INDEX idx_students_status ON public.students (status);

-- 학과 KPI 조회 최적화
CREATE INDEX idx_department_kpis_dept_year ON public.department_kpis (department_id, evaluation_year);

-- 논문 조회 최적화
CREATE INDEX idx_publications_department_id ON public.publications (department_id);
CREATE INDEX idx_publications_date ON public.publications (publication_date);

-- 연구 과제 조회 최적화
CREATE INDEX idx_research_projects_department_id ON public.research_projects (department_id);

-- 프로젝트 집행 조회 최적화
CREATE INDEX idx_project_expenses_project_id ON public.project_expenses (project_id);
CREATE INDEX idx_project_expenses_status ON public.project_expenses (status);


-- =============================================================================
-- 9. Row Level Security (RLS) 설정
-- =============================================================================

-- 모든 테이블에 RLS 활성화
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.colleges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.department_kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_expenses ENABLE ROW LEVEL SECURITY;

-- profiles 테이블: 자신의 프로필만 조회 가능
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- 데이터 테이블: 인증된 사용자는 모두 조회 가능
CREATE POLICY "Authenticated users can view colleges" ON public.colleges
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view departments" ON public.departments
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view students" ON public.students
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view department_kpis" ON public.department_kpis
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view publications" ON public.publications
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view research_projects" ON public.research_projects
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can view project_expenses" ON public.project_expenses
    FOR SELECT
    TO authenticated
    USING (true);

-- 데이터 수정: 관리자만 가능 (애플리케이션 레벨에서 role 체크 권장)
-- 참고: RLS에서 profiles.role을 직접 체크하는 것은 복잡하므로
-- 백엔드 API에서 role 검증을 수행하는 것을 권장합니다.


-- =============================================================================
-- 완료 메시지
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ 데이터베이스 스키마 마이그레이션 완료!';
    RAISE NOTICE '📊 생성된 테이블: 8개 (profiles, colleges, departments, students, department_kpis, publications, research_projects, project_expenses)';
    RAISE NOTICE '🔒 Row Level Security 활성화됨';
    RAISE NOTICE '⚡ 성능 최적화 인덱스 생성됨';
END $$;
