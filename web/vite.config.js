import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy API requests to Python backend
      '/api': {
        target: 'http://127.0.0.1:8050',
        changeOrigin: true,
        secure: false,
      },
      // Proxy JSON data feeds
      '/data': {
        target: 'http://127.0.0.1:8050',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})