# Railway 배포

## 1. Railway 프로젝트 생성
1. https://railway.app 로그인
2. New Project → Deploy from GitHub repo
3. 저장소 선택

## 2. 환경 변수 설정 (Variables 탭)

### 그대로 복사
```
SUPABASE_URL=https://ujscnqcescdmaglwpnoy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqc2NucWNlc2NkbWFnbHdwbm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwMjExNzIsImV4cCI6MjA3ODU5NzE3Mn0.1AIzU7N1mcB-grTZV7NVQcfgMCXaoVdk1XDeSqNg-zY
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqc2NucWNlc2NkbWFnbHdwbm95Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzAyMTE3MiwiZXhwIjoyMDc4NTk3MTcyfQ.WJEfGwuOSmb7Ec1bpqbHco9g41grvlYS9PU96tL487U
SUPABASE_JWT_SECRET=cLISBA9Dt7/LD8h+ZMNIWguT6epXJ6k770Yn+YVAF3njj56ajaAamKoD1h/Jbb2V6g9TvMRzRX7Y17SYtFIZvQ==
DATABASE_URL=postgresql://postgres.ujscnqcescdmaglwpnoy:qkrtjdgh0903@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres
MAX_UPLOAD_SIZE=10485760
VITE_SUPABASE_URL=https://ujscnqcescdmaglwpnoy.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVqc2NucWNlc2NkbWFnbHdwbm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwMjExNzIsImV4cCI6MjA3ODU5NzE3Mn0.1AIzU7N1mcB-grTZV7NVQcfgMCXaoVdk1XDeSqNg-zY
```

### 새로 추가
```
DJANGO_SECRET_KEY=cj78u-%=-^6k&xri_t@njz014ppcqmou4hc_ab)jzi3jkbl3_u
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.railway.app
CORS_ALLOWED_ORIGINS=https://temp
VITE_API_BASE_URL=https://temp/api/v1
```

## 3. 배포 대기
- Deployments 탭에서 빌드 완료 확인 (5-10분)

## 4. 도메인 받기
- Settings → Generate Domain
- 생성된 도메인 복사 (예: abc123.up.railway.app)

## 5. 환경 변수 업데이트
받은 도메인으로 2개 수정:
```
CORS_ALLOWED_ORIGINS=https://abc123.up.railway.app
VITE_API_BASE_URL=https://abc123.up.railway.app/api/v1
```

## 6. 완료
https://abc123.up.railway.app 접속
