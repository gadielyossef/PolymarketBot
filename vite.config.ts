import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    // 🔥 A MÁGICA ESTÁ AQUI: O Proxy para o Backend
    proxy: {
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      },
      '/markets': 'http://127.0.0.1:8000',
      '/start': 'http://127.0.0.1:8000',
      '/stop': 'http://127.0.0.1:8000',
    }
  }
});