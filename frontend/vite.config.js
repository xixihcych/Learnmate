import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // 让 Vite 开发服务器可以读取你 .cursor 目录下的图片资源（登录页展示用）
    fs: {
      allow: ['/home/wangzy/.cursor/projects/home-wangzy-Desktop-Learnmate/assets'],
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})






