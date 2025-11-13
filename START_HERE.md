# 🚀 여기서 시작하세요!

모든 패키지가 설치되었습니다! 이제 3단계만 거치면 프로젝트를 실행할 수 있습니다.

## ✅ 이미 완료된 것
- [x] 백엔드 패키지 설치 완료
- [x] 프론트엔드 패키지 설치 완료
- [x] 프로젝트 코드 구현 완료

## 📋 지금 해야 할 3가지

### 1️⃣ Supabase 프로젝트 생성 (2분)

1. https://supabase.com 접속 → 로그인
2. "New Project" 클릭
3. 정보 입력:
   - Name: `vibemafia` (아무거나)
   - Password: **기억할 비밀번호** 입력
   - Region: Northeast Asia (Seoul)
4. "Create new project" 클릭 → 2분 대기

### 2️⃣ .env 파일 생성 (3분)

#### A. Supabase 정보 복사

프로젝트 생성 후 Dashboard에서:

**① Project URL**
- Settings > API > Configuration > Project URL
- 예: `https://abcdefgh.supabase.co`

**② Anon Key**
- Settings > API > Project API keys > `anon` `public` key
- 예: `eyJhbGciOiJIUzI1NiI...`

**③ Service Role Key**
- 같은 페이지에서 `service_role` key 복사

**④ Database URL**
- Settings > Database > Connection string
- "URI" 탭 선택
- Mode: "Session"
- `[YOUR-PASSWORD]`를 실제 비밀번호로 변경
- 예: `postgresql://postgres:mypass123@db.abcdefgh.supabase.co:5432/postgres`

#### B. backend/.env 파일 생성

`backend/.env` 파일을 만들고 다음 내용 붙여넣기:

```env
SECRET_KEY=django-insecure-test-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

SUPABASE_URL=여기에_①_붙여넣기
SUPABASE_KEY=여기에_②_붙여넣기
SUPABASE_SERVICE_KEY=여기에_③_붙여넣기
DATABASE_URL=여기에_④_붙여넣기

CORS_ALLOWED_ORIGINS=http://localhost:5173
MAX_UPLOAD_SIZE=10485760
```

#### C. frontend/.env 파일 생성

`frontend/.env` 파일을 만들고 다음 내용 붙여넣기:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=여기에_①_붙여넣기
VITE_SUPABASE_ANON_KEY=여기에_②_붙여넣기
```

### 3️⃣ 데이터베이스 및 사용자 설정 (3분)

#### A. 데이터베이스 마이그레이션

터미널에서:
```bash
cd backend
python manage.py migrate
```

✅ "Applying users.0001_initial... OK" 등 메시지 확인

#### B. 테스트 사용자 생성

**① Supabase에서 사용자 생성**
1. Supabase Dashboard > Authentication > Users
2. "Add user" > "Create new user" 클릭
3. 정보 입력:
   - Email: `admin@test.com`
   - Password: `test1234`
   - Auto Confirm User: **체크** ✅
4. "Create user" 클릭
5. **생성된 사용자의 UUID 복사** (클릭하면 복사됨)
   - 예: `12345678-1234-1234-1234-123456789abc`

**② Django에서 Profile 생성**
터미널에서:
```bash
python create_test_user.py
```

1. "1" 입력 (관리자 사용자 생성)
2. 복사한 UUID 붙여넣기 + Enter
3. "✅ 관리자 사용자 생성 완료!" 메시지 확인
4. "4" 입력 (종료)

---

## 🎮 이제 실행하세요!

### 터미널 1 - 백엔드 실행
```bash
cd backend
python manage.py runserver
```
✅ "Starting development server at http://127.0.0.1:8000/" 확인

### 터미널 2 - 프론트엔드 실행
```bash
cd frontend
npm run dev
```
✅ "Local: http://localhost:5173/" 확인

### 브라우저에서 접속
```
http://localhost:5173
```

### 로그인
- Email: `admin@test.com`
- Password: `test1234`

---

## 🎉 성공!

로그인 후 대시보드가 보이면 성공입니다!

## 📝 테스트 시나리오

### 1. 로그인/로그아웃
- ✅ 로그인 페이지에서 admin@test.com로 로그인
- ✅ 대시보드로 자동 이동
- ✅ 헤더에 이메일 표시 확인
- ✅ "로그아웃" 버튼 클릭하여 로그아웃

### 2. 대시보드 (데이터 없는 상태)
- ✅ 4개의 차트 영역 확인
- ✅ "데이터가 없습니다" 메시지 표시

### 3. 데이터 업로드 (관리자 전용)
- ✅ 헤더에서 "데이터 업로드" 메뉴 클릭
- ✅ 파일 드래그 앤 드롭 영역 확인
- ✅ 엑셀 파일 업로드 테스트 가능

### 4. 권한 테스트
일반 사용자 생성 후:
- ✅ "데이터 업로드" 메뉴 표시 안 됨
- ✅ /upload URL 직접 접근 시 권한 오류

---

## ❌ 문제가 생겼나요?

### "No such table: users_profile"
```bash
cd backend
python manage.py migrate
```

### "password authentication failed"
→ `backend/.env`의 `DATABASE_URL`에서 비밀번호를 다시 확인하세요

### "Network Error" (프론트엔드)
→ 백엔드 서버가 http://localhost:8000 에서 실행 중인지 확인

### "401 Unauthorized"
→ Profile이 생성되었는지 확인:
```bash
cd backend
python create_test_user.py
# 3번 선택하여 사용자 목록 확인
```

### Supabase 연결 오류
→ `.env` 파일의 SUPABASE_URL, SUPABASE_KEY가 정확한지 확인

---

## 📚 더 알아보기

- **상세 가이드**: `SETUP_GUIDE.md`
- **빠른 가이드**: `QUICK_START.md`
- **프로젝트 문서**: `/docs/` 폴더

---

## 💡 팁

### 백엔드 테스트 실행
```bash
cd backend
pytest
```

### Django Admin 접속
1. 슈퍼유저 생성:
```bash
python manage.py createsuperuser
```
2. http://localhost:8000/admin 접속

### API 직접 테스트
```bash
# 로그인
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"test1234"}'
```

---

**축하합니다! 🎉 모든 준비가 완료되었습니다!**
