# 프로젝트 테스트 실행 가이드

## 📋 사전 준비사항

- Python 3.10 이상
- Node.js 18 이상
- Supabase 계정 및 프로젝트

## 1단계: Supabase 프로젝트 설정

### 1.1 Supabase 프로젝트 생성
1. https://supabase.com 접속 후 로그인
2. "New Project" 클릭
3. 프로젝트 정보 입력:
   - Project name: `vibemafia-dashboard` (또는 원하는 이름)
   - Database Password: 안전한 비밀번호 입력
   - Region: 가까운 지역 선택
4. "Create new project" 클릭 (약 2분 소요)

### 1.2 Supabase 정보 수집
프로젝트 생성 후 다음 정보를 복사해두세요:

1. **Project URL**:
   - Settings > API > Configuration > Project URL
   - 예: `https://abcdefgh.supabase.co`

2. **API Keys**:
   - Settings > API > Project API keys
   - `anon` `public` key 복사
   - 예: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. **Database Connection String**:
   - Settings > Database > Connection string > URI
   - Mode를 "Session"으로 변경
   - 비밀번호를 실제 비밀번호로 변경
   - 예: `postgresql://postgres:your-password@db.abcdefgh.supabase.co:5432/postgres`

### 1.3 Authentication 설정
1. Authentication > Providers로 이동
2. "Email" provider가 활성화되어 있는지 확인
3. "Confirm email" 옵션을 **비활성화** (테스트 목적)

## 2단계: 백엔드 환경 설정

### 2.1 .env 파일 생성
`backend/.env` 파일을 다음 내용으로 생성:

```bash
# Django 설정
SECRET_KEY=django-insecure-test-key-12345678901234567890
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co  # 여기에 실제 URL 입력
SUPABASE_KEY=your-anon-key                      # 여기에 실제 anon key 입력
SUPABASE_SERVICE_KEY=your-service-key           # 여기에 실제 service key 입력

# 데이터베이스 (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres  # 실제 연결 문자열 입력

# CORS 설정
CORS_ALLOWED_ORIGINS=http://localhost:5173

# 파일 업로드 설정
MAX_UPLOAD_SIZE=10485760
```

### 2.2 가상환경 생성 및 패키지 설치
```bash
cd backend

# 가상환경 생성 (이미 있다면 건너뛰기)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2.3 데이터베이스 마이그레이션
```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 실행
python manage.py migrate
```

## 3단계: Supabase에 테스트 사용자 생성

### 3.1 관리자 사용자 생성
Supabase Dashboard에서:
1. Authentication > Users로 이동
2. "Add user" > "Create new user" 클릭
3. 사용자 정보 입력:
   - Email: `admin@test.com`
   - Password: `test1234` (또는 원하는 비밀번호)
   - Auto Confirm User: **체크**
4. "Create user" 클릭
5. 생성된 사용자의 UUID 복사

### 3.2 Django에서 Profile 생성
```bash
# Django shell 실행
python manage.py shell
```

Shell에서 다음 명령 실행:
```python
from apps.users.models import Profile

# 위에서 복사한 UUID 사용
Profile.objects.create(
    user_id='복사한-UUID',  # Supabase 사용자 UUID
    email='admin@test.com',
    role='admin'
)

# 확인
print(Profile.objects.all())

# 종료
exit()
```

### 3.3 일반 사용자 생성 (선택)
같은 방법으로 일반 사용자도 생성:
- Email: `user@test.com`
- Password: `test1234`
- role: `'user'` (admin 대신)

## 4단계: 프론트엔드 환경 설정

### 4.1 .env 파일 생성
`frontend/.env` 파일을 다음 내용으로 생성:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co  # 실제 URL 입력
VITE_SUPABASE_ANON_KEY=your-anon-key                # 실제 anon key 입력
```

### 4.2 패키지 설치
```bash
cd frontend
npm install
```

## 5단계: 서버 실행

### 5.1 백엔드 서버 실행 (터미널 1)
```bash
cd backend
venv\Scripts\activate  # Windows
python manage.py runserver
```

서버가 http://127.0.0.1:8000/ 에서 실행됩니다.

### 5.2 프론트엔드 서버 실행 (터미널 2)
```bash
cd frontend
npm run dev
```

서버가 http://localhost:5173/ 에서 실행됩니다.

## 6단계: 테스트 실행

### 6.1 백엔드 단위 테스트
```bash
cd backend
venv\Scripts\activate  # Windows
pytest
```

### 6.2 수동 테스트 시나리오

#### 로그인 페이지 테스트
1. 브라우저에서 http://localhost:5173 접속
2. 자동으로 로그인 페이지로 이동
3. 테스트 계정으로 로그인:
   - Email: `admin@test.com`
   - Password: `test1234`
4. 로그인 성공 시 대시보드로 리디렉션

#### 대시보드 페이지 테스트
1. 로그인 후 자동으로 대시보드 페이지 표시
2. 데이터가 없으므로 "데이터가 없습니다" 메시지 표시 확인
3. 4개의 차트 영역이 모두 렌더링되는지 확인

#### 데이터 업로드 페이지 테스트
1. 헤더에서 "데이터 업로드" 메뉴 클릭 (관리자만 표시)
2. 엑셀 파일 드래그 앤 드롭 또는 파일 선택
3. 테스트 파일: `/docs/input_data/` 폴더의 CSV 파일을 XLSX로 변환하여 업로드
4. 업로드 성공 후 대시보드에서 데이터 확인

#### 로그아웃 테스트
1. 헤더에서 "로그아웃" 버튼 클릭
2. 로그인 페이지로 리디렉션 확인
3. 직접 URL로 대시보드 접근 시도 → 로그인 페이지로 리디렉션

## 7단계: API 직접 테스트 (선택)

### 7.1 로그인 API 테스트
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"test1234"}'
```

### 7.2 프로필 조회 API 테스트
```bash
# 위에서 받은 access_token 사용
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer your-access-token"
```

### 7.3 대시보드 API 테스트
```bash
curl -X GET http://localhost:8000/api/v1/dashboard/summary/ \
  -H "Authorization: Bearer your-access-token"
```

## 문제 해결

### 백엔드 오류

#### "No such table: users_profile"
→ 마이그레이션을 실행하지 않았습니다.
```bash
python manage.py migrate
```

#### "FATAL: password authentication failed"
→ DATABASE_URL의 비밀번호가 잘못되었습니다. Supabase에서 다시 확인하세요.

#### "ImportError: No module named 'xxx'"
→ 패키지 설치가 누락되었습니다.
```bash
pip install -r requirements.txt
```

### 프론트엔드 오류

#### "Cannot find module 'xxx'"
→ npm 패키지 설치가 필요합니다.
```bash
npm install
```

#### "Network Error" 또는 CORS 오류
→ 백엔드 서버가 실행 중인지 확인하고, CORS 설정을 확인하세요.

#### "401 Unauthorized"
→ 로그인이 필요하거나 토큰이 만료되었습니다. 다시 로그인하세요.

### Supabase 오류

#### "Invalid JWT"
→ SUPABASE_KEY가 올바른지 확인하세요.

#### "User not found"
→ Supabase에서 사용자를 생성하고 Django Profile도 생성했는지 확인하세요.

## 체크리스트

프로젝트가 제대로 설정되었는지 확인:

- [ ] Supabase 프로젝트 생성 완료
- [ ] `backend/.env` 파일 생성 및 설정
- [ ] `frontend/.env` 파일 생성 및 설정
- [ ] 백엔드 패키지 설치 완료
- [ ] 프론트엔드 패키지 설치 완료
- [ ] 데이터베이스 마이그레이션 실행
- [ ] Supabase에 테스트 사용자 생성
- [ ] Django Profile 생성
- [ ] 백엔드 서버 실행 중 (http://localhost:8000)
- [ ] 프론트엔드 서버 실행 중 (http://localhost:5173)
- [ ] 로그인 성공
- [ ] 대시보드 페이지 접근 가능
- [ ] 데이터 업로드 페이지 접근 가능 (관리자만)

모든 항목이 체크되면 프로젝트 테스트 준비가 완료되었습니다!

## 추가 정보

- **백엔드 API 문서**: http://localhost:8000/api/v1/
- **Supabase Dashboard**: https://supabase.com/dashboard
- **프로젝트 문서**: `/docs/` 폴더 참고
