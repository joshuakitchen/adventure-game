import { defineConfig } from 'vite'
import solidPlugin from 'vite-plugin-solid'
import tsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [solidPlugin(), tsConfigPaths()],
  server: {
    port: 3000,
  },
  build: {
    rollupOptions: {
      input: {
        app: './templates/index.html',
      },
    },
    target: 'esnext',
  },
})
