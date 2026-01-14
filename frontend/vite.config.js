import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || (process.env.NODE_ENV === 'production' ? 'http://localhost:8000' : 'http://backend:8000'),
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
