# Supabase 마이그레이션 가이드

이 디렉토리는 Supabase 데이터베이스 스키마 마이그레이션 파일을 포함합니다.

## 📁 구조

```
supabase/
└── migrations/
    └── 20250113000000_initial_schema.sql    # 초기 데이터베이스 스키마
```

## 🚀 마이그레이션 실행 방법

### 방법 1: Supabase Dashboard (권장)

1. **Supabase Dashboard 접속**
   - https://supabase.com/dashboard
   - 프로젝트 선택

2. **SQL Editor 열기**
   - 왼쪽 메뉴에서 "SQL Editor" 클릭

3. **마이그레이션 SQL 실행**
   - "New query" 클릭
   - `migrations/20250113000000_initial_schema.sql` 파일 내용 전체 복사
   - SQL Editor에 붙여넣기
   - "Run" 버튼 클릭 (또는 Ctrl+Enter)

4. **결과 확인**
   ```
   ✅ 데이터베이스 스키마 마이그레이션 완료!
   📊 생성된 테이블: 8개
   🔒 Row Level Security 활성화됨
   ⚡ 성능 최적화 인덱스 생성됨
   ```

5. **테이블 확인**
   - 왼쪽 메뉴에서 "Table Editor" 클릭
   - 다음 테이블들이 생성되었는지 확인:
     - profiles
     - colleges
     - departments
     - students
     - department_kpis
     - publications
     - research_projects
     - project_expenses

### 방법 2: Supabase CLI (고급 사용자)

```bash
# Supabase CLI 설치
npm install -g supabase

# 프로젝트 초기화
supabase init

# 로컬 개발 환경 시작
supabase start

# 마이그레이션 실행
supabase db push

# 원격 Supabase에 배포
supabase link --project-ref your-project-ref
supabase db push
```

## 📊 생성되는 데이터베이스 구조

### 테이블 목록

1. **profiles** - 사용자 프로필
   - Supabase Auth와 연동
   - 역할 기반 권한 관리 (admin/general)

2. **colleges** - 단과대학 정보
3. **departments** - 학과 정보
4. **students** - 학생 명단
5. **department_kpis** - 학과별 KPI
6. **publications** - 논문 목록
7. **research_projects** - 연구 과제
8. **project_expenses** - 과제 집행 내역

### ERD (Entity Relationship Diagram)

```
profiles (사용자)
    ↓
colleges (단과대학)
    ↓
departments (학과)
    ↓
    ├── students (학생)
    ├── department_kpis (KPI)
    ├── publications (논문)
    └── research_projects (과제)
            ↓
        project_expenses (집행내역)
```

## 🔒 보안 설정

### Row Level Security (RLS)

모든 테이블에 RLS가 활성화되어 있습니다:

- **profiles**: 자신의 프로필만 조회/수정 가능
- **데이터 테이블**: 인증된 사용자는 모두 조회 가능
- **데이터 수정**: 백엔드 API에서 관리자 권한 체크

### 권한 관리

```sql
-- 인증된 사용자는 데이터 조회 가능
TO authenticated USING (true)

-- 자신의 프로필만 접근 가능
USING (auth.uid() = id)
```

## ⚡ 성능 최적화

### 생성된 인덱스

- **departments**: college_id
- **students**: department_id, status
- **department_kpis**: department_id + evaluation_year
- **publications**: department_id, publication_date
- **research_projects**: department_id
- **project_expenses**: project_id, status

### 쿼리 최적화 팁

```sql
-- 학과별 학생 수 조회 (인덱스 활용)
SELECT d.name, COUNT(s.id)
FROM departments d
LEFT JOIN students s ON s.department_id = d.id
GROUP BY d.name;

-- 연도별 논문 수 조회 (인덱스 활용)
SELECT EXTRACT(YEAR FROM publication_date) as year, COUNT(*)
FROM publications
GROUP BY year
ORDER BY year;
```

## 🧪 테스트

### 마이그레이션 검증

```sql
-- 1. 테이블 존재 확인
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. ENUM 타입 확인
SELECT typname
FROM pg_type
WHERE typtype = 'e';

-- 3. RLS 확인
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';

-- 4. 인덱스 확인
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename;
```

### 샘플 데이터 삽입

```sql
-- 단과대학 추가
INSERT INTO colleges (name) VALUES ('공과대학'), ('자연과학대학');

-- 학과 추가
INSERT INTO departments (college_id, name)
SELECT id, '컴퓨터공학과' FROM colleges WHERE name = '공과대학';

-- 학생 추가
INSERT INTO students (
    student_id_number, name, department_id,
    program_level, status, grade
)
SELECT '2024001', '홍길동', id, '학사', '재학', 3
FROM departments WHERE name = '컴퓨터공학과';
```

## 🔄 마이그레이션 롤백

마이그레이션을 되돌리려면:

```sql
-- 모든 테이블 삭제
DROP TABLE IF EXISTS public.project_expenses CASCADE;
DROP TABLE IF EXISTS public.research_projects CASCADE;
DROP TABLE IF EXISTS public.publications CASCADE;
DROP TABLE IF EXISTS public.department_kpis CASCADE;
DROP TABLE IF EXISTS public.students CASCADE;
DROP TABLE IF EXISTS public.departments CASCADE;
DROP TABLE IF EXISTS public.colleges CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- ENUM 타입 삭제
DROP TYPE IF EXISTS public.user_role CASCADE;
DROP TYPE IF EXISTS public.academic_program CASCADE;
DROP TYPE IF EXISTS public.academic_status CASCADE;
DROP TYPE IF EXISTS public.project_status CASCADE;
```

## 📝 다음 단계

마이그레이션 완료 후:

1. ✅ Django 마이그레이션 실행
   ```bash
   cd backend
   python manage.py migrate
   ```

2. ✅ 테스트 사용자 생성
   - Supabase Dashboard > Authentication > Users
   - 사용자 생성 후 UUID 복사
   - `python create_test_user.py`로 Profile 생성

3. ✅ 애플리케이션 테스트
   - 백엔드 서버 실행: `python manage.py runserver`
   - 프론트엔드 서버 실행: `npm run dev`
   - 로그인 테스트

## ❓ FAQ

### Q: Django 마이그레이션과 어떻게 다른가요?
**A:**
- Supabase 마이그레이션: Supabase 데이터베이스에 직접 스키마 생성
- Django 마이그레이션: Django ORM을 통해 스키마 생성
- 둘 중 하나만 실행하면 됩니다. (Supabase 마이그레이션 권장)

### Q: 마이그레이션을 다시 실행할 수 있나요?
**A:** 네, SQL 파일에 `DROP TABLE IF EXISTS`가 포함되어 있어 안전하게 재실행 가능합니다.

### Q: 프로덕션 환경에서도 사용 가능한가요?
**A:** 네, 하지만 프로덕션에서는:
- `DROP TABLE` 명령어 제거 권장
- 백업 먼저 수행
- 단계적 마이그레이션 고려

### Q: RLS 정책을 수정하고 싶어요.
**A:** Supabase Dashboard > Authentication > Policies에서 GUI로 수정하거나, SQL로 직접 수정 가능합니다.

## 🔗 관련 문서

- [Supabase 공식 문서](https://supabase.com/docs)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [프로젝트 데이터베이스 설계](/docs/database.md)
- [프로젝트 아키텍처](/docs/architecture.md)

## 📞 문제 해결

문제가 발생하면:
1. Supabase Dashboard > Logs 확인
2. SQL 오류 메시지 확인
3. `/docs/database.md` 스키마 설계 참고
4. GitHub Issues에 문의
