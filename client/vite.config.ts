import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: 'localhost',  // Changed from 127.0.0.1 to localhost
    port: 5173,  // Changed from 8000 to default Vite port
    strictPort: false,  // Allow fallback to other ports if 5173 is busy
  },
  preview: {
    host: '127.0.0.1',
    port: 8001,
    strictPort: true,
  },
})
