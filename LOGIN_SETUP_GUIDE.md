# 로그인 페이지 구현 완료 가이드

## 구현 완료 항목

### 백엔드 (Django + DRF)

#### 1. Repository 레이어
- `apps/users/repositories.py` - ProfileRepository 구현
  - `get_by_id()`: UUID로 프로필 조회
  - `get_by_email()`: 이메일로 프로필 조회
  - `create_profile()`: 새 프로필 생성

#### 2. Serializers
- `apps/users/serializers.py`
  - `LoginSerializer`: 로그인 요청 데이터 검증
  - `ProfileSerializer`: 프로필 응답 데이터 직렬화

#### 3. Views (API 엔드포인트)
- `apps/users/views.py`
  - `LoginView` (POST /api/v1/auth/login/): Supabase Auth 로그인
  - `ProfileView` (GET /api/v1/auth/profile/): 사용자 프로필 조회
  - `LogoutView` (POST /api/v1/auth/logout/): 로그아웃

#### 4. URL 라우팅
- `apps/users/urls.py`: 인증 관련 URL 패턴
- `dashboard_project/urls.py`: 프로젝트 전역 URL에 통합

#### 5. 테스트
- `apps/users/tests/test_repositories.py`: Repository 단위 테스트
- `apps/users/tests/test_login_api.py`: 로그인 API 통합 테스트
- `apps/users/tests/test_profile_api.py`: 프로필 API 테스트

---

### 프론트엔드 (React + Vite)

#### 1. API Client
- `src/api/index.js`: Axios 인스턴스 (JWT 자동 추가, 401 처리)
- `src/api/authAPI.js`: 인증 관련 API 함수
  - `login()`: 로그인
  - `logout()`: 로그아웃
  - `getProfile()`: 프로필 조회

#### 2. 전역 상태 관리
- `src/store/authStore.js`: Zustand 기반 인증 상태
  - `user`: 사용자 정보
  - `isAuthenticated`: 로그인 여부
  - `setUser()`: 사용자 정보 저장
  - `logout()`: 로그아웃
  - `isAdmin()`: 관리자 여부 확인

#### 3. 커스텀 훅
- `src/hooks/useAuth.js`: 로그인/로그아웃 비즈니스 로직
  - Supabase Auth 호출
  - 프로필 조회 및 role 정보 가져오기
  - 전역 상태 업데이트
  - 자동 리디렉션

#### 4. 컴포넌트
- `src/components/common/Input.jsx`: 공통 입력 필드
- `src/components/common/Button.jsx`: 공통 버튼
- `src/components/common/ErrorMessage.jsx`: 에러 메시지
- `src/components/auth/ProtectedRoute.jsx`: 인증 가드

#### 5. 페이지
- `src/pages/LoginPage.jsx`: 로그인 페이지
  - 이메일/비밀번호 입력
  - 유효성 검사
  - 로그인 처리
  - 에러 표시
  - 이미 로그인된 사용자 자동 리디렉션

#### 6. 라우팅
- `src/App.jsx`: React Router 설정
  - `/login`: 로그인 페이지
  - `/dashboard`: 대시보드 (보호된 라우트)
  - `/upload`: 데이터 업로드 (관리자 전용)

---

## 설정 방법

### 1. 백엔드 환경 변수 설정

`backend/.env` 파일 생성:

```bash
# Django 설정
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# 데이터베이스
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 2. 프론트엔드 환경 변수 설정

`frontend/.env` 파일 생성:

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 3. 의존성 설치

**백엔드:**
```bash
cd backend
pip install -r requirements.txt
```

**프론트엔드:**
```bash
cd frontend
npm install
```

### 4. 데이터베이스 마이그레이션

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 5. 테스트 관리자 계정 생성 (Supabase)

1. Supabase 대시보드에서 Authentication > Users 메뉴로 이동
2. "Add user" 버튼 클릭
3. 이메일과 비밀번호 입력
4. 생성된 사용자의 UUID를 확인
5. Django Shell에서 프로필 생성:

```python
python manage.py shell

from apps.users.models import Profile, UserRole
Profile.objects.create(
    id='여기에-supabase-user-uuid',
    role=UserRole.ADMIN,
    email='admin@example.com',
    username='관리자'
)
```

### 6. 서버 실행

**백엔드:**
```bash
cd backend
python manage.py runserver
```

**프론트엔드:**
```bash
cd frontend
npm run dev
```

### 7. 테스트 실행

**백엔드 테스트:**
```bash
cd backend
pytest
```

**프론트엔드 테스트:**
```bash
cd frontend
npm run test
```

---

## API 엔드포인트

### 로그인
```
POST /api/v1/auth/login/

Request:
{
  "email": "admin@example.com",
  "password": "password123"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "user": {
    "id": "uuid-here",
    "email": "admin@example.com"
  }
}
```

### 프로필 조회
```
GET /api/v1/auth/profile/
Header: Authorization: Bearer {access_token}

Response (200 OK):
{
  "id": "uuid-here",
  "email": "admin@example.com",
  "role": "admin",
  "username": "관리자",
  "created_at": "2025-11-13T00:00:00Z"
}
```

### 로그아웃
```
POST /api/v1/auth/logout/
Header: Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "로그아웃되었습니다."
}
```

---

## 에러 코드

| HTTP 상태 | 에러 코드 | 설명 |
|----------|----------|------|
| 400 | VALIDATION_ERROR | 입력 데이터 형식 오류 |
| 401 | INVALID_CREDENTIALS | 자격 증명 불일치 |
| 401 | UNAUTHORIZED | 인증 정보 없음 |
| 404 | ROLE_NOT_FOUND | 프로필 조회 실패 |
| 500 | SERVER_ERROR | 서버 내부 오류 |

---

## 데이터 플로우

### 로그인 성공 플로우
1. 사용자가 이메일/비밀번호 입력
2. LoginPage → useAuth.login()
3. authAPI.login() → 백엔드 POST /api/v1/auth/login/
4. 백엔드 → Supabase Auth sign_in_with_password()
5. Supabase 인증 성공 → access_token, refresh_token 반환
6. 프론트엔드 → authAPI.getProfile() 호출
7. 백엔드 → profiles 테이블에서 role 조회
8. 프론트엔드 → useAuthStore.setUser() (role 포함)
9. navigate('/dashboard') → 자동 리디렉션

---

## TDD 구현 내역

### RED → GREEN → REFACTOR 프로세스 준수

1. **ProfileRepository 테스트 작성** (RED)
   - get_by_id_existing_user
   - get_by_id_non_existing_user
   - create_profile_success
   - get_by_email_existing_user

2. **ProfileRepository 구현** (GREEN)
   - BaseRepository 상속
   - 모든 테스트 통과

3. **Login API 테스트 작성** (RED)
   - test_login_success
   - test_login_invalid_credentials
   - test_login_missing_email
   - test_login_invalid_email_format
   - test_login_short_password

4. **LoginView 구현** (GREEN)
   - Serializer 검증
   - Supabase Auth 통합
   - 에러 처리

5. **프론트엔드 통합**
   - useAuth 훅으로 비즈니스 로직 캡슐화
   - LoginPage에서 UI와 로직 분리
   - ProtectedRoute로 인증 가드

---

## 완료 확인 체크리스트

- [x] 백엔드 Repository 레이어 구현
- [x] 백엔드 Repository 단위 테스트
- [x] 백엔드 Serializers 구현
- [x] 백엔드 Views 구현
- [x] 백엔드 Views 통합 테스트
- [x] 백엔드 URL 라우팅 설정
- [x] 프론트엔드 API Client 구현
- [x] 프론트엔드 전역 상태 관리
- [x] 프론트엔드 공통 컴포넌트
- [x] 프론트엔드 useAuth 훅
- [x] 프론트엔드 LoginPage
- [x] 프론트엔드 라우팅 설정
- [x] 에러 핸들링 완벽 구현
- [x] 이미 로그인된 사용자 리디렉션
- [x] 프로필 조회 및 role 정보 가져오기

---

## 추가 구현 사항 (계획과의 차이점)

### 구현 완료된 추가 기능:
1. **로그인 후 프로필 자동 조회**
   - useAuth 훅에서 로그인 성공 시 자동으로 getProfile() 호출
   - role 정보를 전역 상태에 저장하여 권한 관리 준비

2. **에러 처리 강화**
   - 네트워크 에러 처리
   - 401 응답 시 자동 로그아웃 및 리디렉션
   - 사용자 친화적 에러 메시지

3. **UX 개선**
   - 로딩 상태 표시
   - 이미 로그인된 사용자 자동 리디렉션
   - 입력 필드 검증

---

## 다음 단계

로그인 페이지 구현이 완료되었습니다. 다음 작업을 진행할 수 있습니다:

1. **데이터 업로드 페이지 구현** (UC-002)
2. **메인 대시보드 구현** (UC-003)
3. **E2E 테스트 작성**
4. **배포 준비** (Railway)

---

**작성일:** 2025-11-13
**작성자:** Claude Code Agent
**문서 버전:** 1.0.0
