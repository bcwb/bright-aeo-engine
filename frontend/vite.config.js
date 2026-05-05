import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/runs': 'http://localhost:8000',
      '/config': 'http://localhost:8000',   // covers /config/prompts, /config/competitors, /config/peer_sets, /config/models
      '/recommendations': 'http://localhost:8000',
      '/content': 'http://localhost:8000',
      '/targeting': 'http://localhost:8000',
      '/assets':    'http://localhost:8000',
      '/logs':      'http://localhost:8000',
      '/me':        'http://localhost:8000',
    },
  },
})
