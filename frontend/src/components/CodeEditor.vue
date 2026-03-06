<template>
  <div id="editor"></div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import * as monaco from 'monaco-editor'
import { useCameraLayoutStore } from '../stores/cameraLayout'

const store = useCameraLayoutStore()

onMounted(() => {
  const editor = monaco.editor.create(document.getElementById('editor'), {
    value: '<div>Hello world</div>',
    language: 'html',
    theme: store.editorTheme,
    automaticLayout: true
  })

  store.setEditorInstance(editor)

  watch(() => store.editorTheme, (newTheme) => {
    store.setTheme(newTheme)
  })
})
</script>

<style scoped>
#editor {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
