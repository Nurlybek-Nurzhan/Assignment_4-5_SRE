import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const SERVICES = {
  '/api/auth/':     'http://localhost:8001',
  '/api/products/': 'http://localhost:8002',
  '/api/orders/':   'http://localhost:8003',
  '/api/users/':    'http://localhost:8004',
  '/api/chat/':     'http://localhost:8005',
  '/api/payments/': 'http://localhost:8006',
}

const proxy = Object.fromEntries(
  Object.entries(SERVICES).map(([prefix, target]) => [
    prefix,
    {
      target,
      changeOrigin: true,
      rewrite: path => path.replace(new RegExp(`^${prefix}`), '/'),
    },
  ])
)

export default defineConfig({
  plugins: [react()],
  build: { outDir: 'dist' },
  server: { proxy },
})
