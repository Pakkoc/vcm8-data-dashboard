# Railway 환경 변수 설정 가이드

Railway 배포 시 설정해야 할 환경 변수 목록입니다.

## 필수 환경 변수

### 1. Django 설정
```bash
DJANGO_SECRET_KEY=<랜덤한 50자 이상의 문자열>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<Railway에서 제공하는 도메인>,<커스텀 도메인>
```

**DJANGO_SECRET_KEY 생성 방법:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. 데이터베이스 (Supabase)
```bash
DATABASE_URL=postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres
```

**주의:** Supabase Connection Pooler URL을 사용하세요 (IPv4 호환)

### 3. Supabase 인증
```bash
SUPABASE_URL=https://<PROJECT_REF>.supabase.co
SUPABASE_KEY=<SUPABASE_ANON_KEY>
SUPABASE_SERVICE_KEY=<SUPABASE_SERVICE_ROLE_KEY>
SUPABASE_JWT_SECRET=<SUPABASE_JWT_SECRET>
```

**Supabase 설정 위치:**
- Dashboard → Project Settings → API
- `SUPABASE_URL`: Project URL
- `SUPABASE_KEY`: `anon` `public`
- `SUPABASE_SERVICE_KEY`: `service_role` `secret` (주의: 노출 금지)
- `SUPABASE_JWT_SECRET`: JWT Settings → JWT Secret

### 4. 프론트엔드 API URL
```bash
VITE_API_BASE_URL=https://<YOUR_RAILWAY_DOMAIN>/api/v1
VITE_SUPABASE_URL=https://<PROJECT_REF>.supabase.co
VITE_SUPABASE_KEY=<SUPABASE_ANON_KEY>
```

**주의:** `VITE_`로 시작하는 변수는 React 빌드 시 포함됩니다.

---

## 선택적 환경 변수

### 1. CORS 설정
```bash
CORS_ALLOWED_ORIGINS=https://<YOUR_RAILWAY_DOMAIN>
```

기본값: `http://localhost:5173` (개발 환경용)
**배포 시 Railway 도메인으로 변경 필요**

### 2. 파일 업로드 제한
```bash
MAX_UPLOAD_SIZE=10485760
```

기본값: 10MB (10485760 bytes)

---

## Railway에서 환경 변수 설정하는 방법

### 방법 1: Railway Dashboard (추천)
1. Railway 프로젝트 선택
2. 서비스 클릭
3. **Variables** 탭 선택
4. **New Variable** 버튼 클릭
5. 위의 환경 변수들을 하나씩 추가

### 방법 2: Railway CLI
```bash
railway variables set DJANGO_SECRET_KEY="<YOUR_SECRET_KEY>"
railway variables set DATABASE_URL="<YOUR_DATABASE_URL>"
...
```

---

## 환경 변수 확인 체크리스트

배포 전에 다음 환경 변수들이 모두 설정되었는지 확인하세요:

- [ ] `DJANGO_SECRET_KEY`
- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_ALLOWED_HOSTS`
- [ ] `DATABASE_URL`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `SUPABASE_SERVICE_KEY`
- [ ] `SUPABASE_JWT_SECRET`
- [ ] `VITE_API_BASE_URL`
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_KEY`
- [ ] `CORS_ALLOWED_ORIGINS`

---

## 보안 주의사항

1. **절대 Git에 커밋하지 마세요:**
   - `.env` 파일
   - `SUPABASE_SERVICE_KEY`
   - `DJANGO_SECRET_KEY`

2. **Production 환경:**
   - `DJANGO_DEBUG=False` 필수
   - `DJANGO_ALLOWED_HOSTS`에 실제 도메인만 포함

3. **CORS 설정:**
   - `CORS_ALLOWED_ORIGINS`에 실제 도메인만 포함
   - 개발용 `localhost` 제거

---

## 배포 후 확인 사항

1. **헬스체크:**
   ```bash
   curl https://<YOUR_RAILWAY_DOMAIN>/api/v1/dashboard/summary/
   ```

2. **Static 파일:**
   ```bash
   curl https://<YOUR_RAILWAY_DOMAIN>/static/index.html
   ```

3. **로그 확인:**
   ```bash
   railway logs
   ```

---

## 문제 해결

### 1. 500 Internal Server Error
- Railway 로그 확인: `railway logs`
- `DJANGO_SECRET_KEY` 설정 확인
- `DATABASE_URL` 형식 확인

### 2. Static 파일이 로드되지 않음
- `railway logs`에서 `collectstatic` 실행 확인
- `STATIC_ROOT` 경로 확인

### 3. API 호출 실패 (CORS)
- `CORS_ALLOWED_ORIGINS`에 Railway 도메인 추가 확인
- 브라우저 콘솔에서 CORS 에러 확인

### 4. 데이터베이스 연결 실패
- Supabase Connection Pooler URL 사용 확인 (IPv4)
- Supabase 프로젝트가 활성 상태인지 확인
