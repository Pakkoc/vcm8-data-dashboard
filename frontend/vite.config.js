import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 루트 디렉토리의 .env 파일 사용
  envDir: path.resolve(__dirname, '..'),
  build: {
    // Django static 폴더로 빌드 결과 출력
    outDir: path.resolve(__dirname, '../backend/staticfiles'),
    emptyOutDir: true,
    // Production 모드에서 source map 생성하지 않음 (보안)
    sourcemap: false,
  },
  // Django에서 /static/ 경로로 서빙할 것이므로 base 설정
  base: '/static/',
})
