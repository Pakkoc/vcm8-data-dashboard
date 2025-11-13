# 빠른 시작 가이드 (5분 안에 실행하기)

이 가이드는 최소한의 단계로 프로젝트를 실행하는 방법을 안내합니다.

## ⚡ 빠른 단계

### 1. Supabase 프로젝트 생성 (2분)

1. https://supabase.com 접속 → 로그인
2. "New Project" 클릭
3. 정보 입력:
   - Name: `vibemafia` (아무거나)
   - Password: 기억할 비밀번호 입력
   - Region: Northeast Asia (Seoul)
4. "Create new project" 클릭 → 2분 대기

### 2. Supabase 정보 복사 (1분)

프로젝트 생성 후:

**A. Project URL 복사:**
- Settings > API > Project URL
- 예: `https://abcdefgh.supabase.co`

**B. API Key 복사:**
- Settings > API > Project API keys
- `anon` `public` key 복사
- 예: `eyJhbGciOiJIUzI1NiI...`

**C. Service Role Key 복사:**
- 같은 페이지에서 `service_role` key 복사

**D. Database URL 복사:**
- Settings > Database > Connection string
- "URI" 탭 선택
- Mode: "Session"
- `[YOUR-PASSWORD]`를 실제 비밀번호로 변경
- 예: `postgresql://postgres:mypassword@db.abcdefgh.supabase.co:5432/postgres`

### 3. .env 파일 생성 (1분)

#### backend/.env 파일:
```bash
SECRET_KEY=django-insecure-test-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

SUPABASE_URL=여기에_Project_URL_붙여넣기
SUPABASE_KEY=여기에_anon_key_붙여넣기
SUPABASE_SERVICE_KEY=여기에_service_role_key_붙여넣기
DATABASE_URL=여기에_Database_URL_붙여넣기

CORS_ALLOWED_ORIGINS=http://localhost:5173
MAX_UPLOAD_SIZE=10485760
```

#### frontend/.env 파일:
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=여기에_Project_URL_붙여넣기
VITE_SUPABASE_ANON_KEY=여기에_anon_key_붙여넣기
```

### 4. 백엔드 설정 및 실행 (1분)

새 터미널 열고:

```bash
cd backend

# 가상환경 활성화
venv\Scripts\activate

# 패키지 설치 (처음 한 번만)
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
```

✅ "Starting development server at http://127.0.0.1:8000/" 메시지 확인

### 5. 프론트엔드 실행 (1분)

**새 터미널** 열고:

```bash
cd frontend

# 패키지 설치 (처음 한 번만)
npm install

# 서버 실행
npm run dev
```

✅ "Local: http://localhost:5173/" 메시지 확인

### 6. 테스트 사용자 생성 (1분)

#### A. Supabase에서 사용자 생성
1. Supabase Dashboard > Authentication > Users
2. "Add user" > "Create new user" 클릭
3. 정보 입력:
   - Email: `admin@test.com`
   - Password: `test1234`
   - Auto Confirm User: **체크**
4. "Create user" 클릭
5. **생성된 사용자의 UUID 복사** (예: `12345678-1234-1234-1234-123456789abc`)

#### B. Django에서 Profile 생성
백엔드 터미널에서 (Ctrl+C로 서버 중단 후):

```bash
python create_test_user.py
```

1. "1" 입력 (관리자 사용자 생성)
2. 복사한 UUID 붙여넣기
3. "4" 입력 (종료)
4. `python manage.py runserver` 다시 실행

### 7. 로그인 테스트 🎉

1. 브라우저에서 http://localhost:5173 접속
2. 로그인:
   - Email: `admin@test.com`
   - Password: `test1234`
3. 성공 시 대시보드로 이동!

---

## ❌ 문제 해결

### "No such table: users_profile"
→ 마이그레이션 실행:
```bash
python manage.py migrate
```

### "password authentication failed"
→ DATABASE_URL의 비밀번호 확인

### "Network Error" (프론트엔드)
→ 백엔드 서버가 실행 중인지 확인 (http://localhost:8000)

### "401 Unauthorized"
→ Profile이 생성되었는지 확인:
```bash
python create_test_user.py
# 3번 선택하여 사용자 목록 확인
```

---

## 📊 테스트 시나리오

### 1. 로그인/로그아웃
- ✅ 로그인 페이지에서 `admin@test.com` / `test1234` 입력
- ✅ 대시보드로 리디렉션
- ✅ 헤더에서 "로그아웃" 클릭
- ✅ 로그인 페이지로 돌아감

### 2. 대시보드 (데이터 없는 상태)
- ✅ 로그인 후 대시보드 페이지 표시
- ✅ 4개 차트 영역에 "데이터가 없습니다" 메시지 표시
- ✅ 헤더에 사용자 이메일 표시

### 3. 데이터 업로드 (관리자만)
- ✅ 헤더에서 "데이터 업로드" 메뉴 클릭
- ✅ 파일 드래그 앤 드롭 영역 표시
- ✅ 엑셀 파일 선택 (.xlsx, .xls만 허용)
- ✅ 업로드 버튼 활성화
- ✅ (실제 데이터 업로드 테스트는 샘플 엑셀 파일 필요)

### 4. 권한 테스트
일반 사용자로 로그인 시 (user@test.com):
- ✅ 대시보드 접근 가능
- ✅ "데이터 업로드" 메뉴 **표시 안 됨**
- ✅ `/upload` URL 직접 접근 시 권한 없음 메시지

---

## 🔧 개발자 도구

### 백엔드 테스트 실행
```bash
cd backend
pytest
```

### API 테스트 (curl)
```bash
# 로그인
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@test.com\",\"password\":\"test1234\"}"
```

### Django Admin 접속
1. 슈퍼유저 생성:
```bash
python manage.py createsuperuser
```

2. http://localhost:8000/admin 접속

---

## 📚 더 자세한 가이드

- 전체 설정 가이드: `SETUP_GUIDE.md`
- 프로젝트 구조: `/docs/structure.md`
- API 문서: `/docs/PRD.md`

성공적으로 실행되었다면 프로젝트가 정상 작동하는 것입니다! 🎉
