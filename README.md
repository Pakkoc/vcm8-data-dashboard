# 데이터 시각화 대시보드

대학 성과 데이터를 시각화하는 웹 대시보드 프로젝트입니다.

## 🚀 빠른 시작

### 1. 환경 변수 설정 (3분)

**프로젝트 루트**에 `.env` 파일 하나만 생성하면 됩니다:

```bash
# .env 파일 생성
cp .env.example .env
```

그 다음 `.env` 파일을 열고 Supabase 정보를 입력하세요.

👉 **상세 가이드:** [SETUP_ENV.md](SETUP_ENV.md)

### 2. 패키지 설치 (이미 완료됨)

```bash
# 백엔드
cd backend
pip install -r requirements.txt

# 프론트엔드
cd frontend
npm install
```

### 3. 데이터베이스 마이그레이션

```bash
cd backend
python manage.py migrate
```

### 4. 테스트 사용자 생성

```bash
cd backend
python create_test_user.py
```

### 5. 서버 실행

**터미널 1 (백엔드):**
```bash
cd backend
python manage.py runserver
```

**터미널 2 (프론트엔드):**
```bash
cd frontend
npm run dev
```

### 6. 브라우저 접속

```
http://localhost:5173
```

**로그인:**
- Email: `admin@test.com`
- Password: `test1234`

---

## 📁 프로젝트 구조

```
08_challenge/
├── .env                    # 환경 변수 (백엔드 + 프론트엔드 공통)
├── backend/                # Django REST API
│   ├── apps/
│   │   ├── users/         # 사용자 인증
│   │   ├── dashboard/     # 대시보드 데이터
│   │   └── data_upload/   # 데이터 업로드
│   └── manage.py
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/    # 공통 컴포넌트
│   │   ├── pages/         # 페이지
│   │   ├── api/           # API 클라이언트
│   │   └── store/         # 전역 상태
│   └── package.json
└── docs/                   # 프로젝트 문서
```

---

## 🎯 주요 기능

### 1. 사용자 인증
- 로그인/로그아웃
- Supabase Auth 기반
- 역할 기반 권한 관리 (관리자/일반 사용자)

### 2. 대시보드
- 4가지 차트 시각화:
  - 학과별 성과 (막대 그래프)
  - 논문 수 추이 (라인 차트)
  - 학생 현황 (파이 차트)
  - 예산 집행률 (게이지 차트)

### 3. 데이터 업로드 (관리자 전용)
- 엑셀 파일 업로드
- 드래그 앤 드롭 지원
- 데이터 검증 및 파싱

---

## 🛠️ 기술 스택

### 백엔드
- Django 5.0
- Django REST Framework
- Supabase (PostgreSQL + Auth)
- Pandas (데이터 처리)
- pytest (테스트)

### 프론트엔드
- React 18
- Vite
- Recharts (차트)
- Zustand (상태 관리)
- TailwindCSS (스타일링)
- Axios (HTTP 클라이언트)

---

## 📚 문서

- **[START_HERE.md](START_HERE.md)** - 처음 시작하는 분들을 위한 가이드
- **[SETUP_ENV.md](SETUP_ENV.md)** - 환경 변수 설정 상세 가이드
- **[QUICK_START.md](QUICK_START.md)** - 5분 안에 실행하기
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - 완전한 설정 및 문제 해결 가이드

### 프로젝트 기획 문서
- `/docs/PRD.md` - 프로젝트 요구사항 정의서
- `/docs/userflow.md` - 사용자 플로우
- `/docs/architecture.md` - 아키텍처 설계
- `/docs/database.md` - 데이터베이스 스키마
- `/docs/usecases/` - 기능별 유스케이스
- `/docs/pages/` - 페이지별 구현 계획

---

## 🧪 테스트

### 백엔드 테스트
```bash
cd backend
pytest
```

### 프론트엔드 테스트
```bash
cd frontend
npm run test
```

---

## 🌟 주요 특징

### 1. TDD 기반 개발
- 테스트 우선 작성 (Red-Green-Refactor)
- 40+ 테스트 케이스
- 높은 테스트 커버리지

### 2. Layered Architecture
- View → Service → Repository → Model
- 단일 책임 원칙
- 높은 유지보수성

### 3. 완벽한 에러 핸들링
- 클라이언트 측 유효성 검사
- 서버 측 예외 처리
- 사용자 친화적 에러 메시지

### 4. 보안
- Supabase Auth 기반 JWT 인증
- 역할 기반 권한 관리
- CORS 설정
- SQL Injection 방지

---

## 🔧 개발 도구

### Django Admin
```bash
# 슈퍼유저 생성
cd backend
python manage.py createsuperuser

# 접속
# http://localhost:8000/admin
```

### API 테스트
```bash
# 로그인
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"test1234"}'

# 대시보드 데이터 조회
curl -X GET http://localhost:8000/api/v1/dashboard/summary/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이센스

This project is licensed under the MIT License.

---

## 💡 FAQ

### Q: 환경 변수 파일은 어디에 두나요?
**A:** 프로젝트 루트 (`08_challenge/`)에 `.env` 파일 하나만 생성하면 됩니다. 백엔드와 프론트엔드가 공통으로 사용합니다.

### Q: 테스트 사용자 비밀번호는 무엇인가요?
**A:**
- Email: `admin@test.com`
- Password: `test1234`

### Q: 데이터가 표시되지 않아요.
**A:** 처음 실행 시에는 데이터가 없습니다. 관리자로 로그인 후 "데이터 업로드" 페이지에서 엑셀 파일을 업로드하세요.

### Q: 프론트엔드/백엔드 중 하나만 실행할 수 있나요?
**A:** 네, 가능합니다. 하지만 전체 기능을 사용하려면 둘 다 실행해야 합니다.

### Q: 다른 포트를 사용하고 싶어요.
**A:**
- 백엔드: `python manage.py runserver 8080`
- 프론트엔드: `vite.config.js`에서 `server.port` 설정

---

## 📞 문제가 있나요?

- **환경 설정 문제:** [SETUP_ENV.md](SETUP_ENV.md)의 문제 해결 섹션 참고
- **실행 문제:** [SETUP_GUIDE.md](SETUP_GUIDE.md)의 문제 해결 섹션 참고
- **버그 리포트:** GitHub Issues에 등록

---

**Happy Coding! 🎉**
