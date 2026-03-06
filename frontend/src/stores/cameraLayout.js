import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
import * as monaco from 'monaco-editor'

export const useCameraLayoutStore = defineStore('cameraLayout', {
  state: () => ({
    topHeight: null,
    bottomHeight: null,
    editorTheme: 'vs-dark',
    cameraActive: true,
    editorInstance: shallowRef(null),
    cameraBackground: '#000000',
    dividerColor: '#444444'
  }),
  actions: {
    setHeights(top, bottom) {
      this.topHeight = top
      this.bottomHeight = bottom
    },
    resetHeights(defaultTop, defaultBottom) {
      this.topHeight = defaultTop
      this.bottomHeight = defaultBottom
    },
    setTheme(theme) {
      this.editorTheme = theme
      monaco.editor.setTheme(theme)

      if (theme === 'vs-light') {
        this.cameraBackground = '#ffffff'
        this.dividerColor = '#cccccc'
      } else {
        this.cameraBackground = '#000000'
        this.dividerColor = '#444444'
      }
    },
    toggleCamera() {
      this.cameraActive = !this.cameraActive
    },
    clearEditor() {
      const editor = this.editorInstance
      if (editor) {
        const model = editor.getModel()
        if (model) {
          model.setValue('')
        }
      }
    },
    exportCode() {
      const editor = this.editorInstance
      if (editor) {
        const model = editor.getModel()
        if (model) {
          const code = model.getValue()
          navigator.clipboard.writeText(code)
          alert('Код скопирован в буфер обмена')
        }
      }
    },
    setEditorInstance(instance) {
      this.editorInstance = instance
    }
  }
})
