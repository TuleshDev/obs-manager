import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import monacoEditorPlugin from 'vite-plugin-monaco-editor'

export default defineConfig({
  plugins: [
    vue(),
    monacoEditorPlugin({
      languageWorkers: ['editorWorkerService', 'html', 'css', 'json', 'typescript']
    })
  ],
  optimizeDeps: {
    include: ['monaco-editor']
  },
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000'
    }
  }
})
