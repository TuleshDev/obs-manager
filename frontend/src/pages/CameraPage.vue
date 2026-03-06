<template>
  <v-app>
    <div id="camera-page">
      <ControlSidebar />

      <div id="split-container">
        <div class="top-pane"
             :style="{ height: topHeight + 'px', background: store.cameraBackground }">
          <CameraView />
        </div>

        <div class="divider"
             @mousedown="startDrag"
             :style="{ background: store.dividerColor }">
        </div>

        <div class="bottom-pane"
             :style="{ height: bottomHeight + 'px' }">
          <CodeEditor />
        </div>
      </div>
    </div>
  </v-app>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCameraLayoutStore } from '../stores/cameraLayout'
import CameraView from '../components/CameraView.vue'
import ControlSidebar from '../components/ControlSidebar.vue'
import CodeEditor from '../components/CodeEditor.vue'

const store = useCameraLayoutStore()

const topHeight = computed(() => store.topHeight)
const bottomHeight = computed(() => store.bottomHeight)

let isDragging = false

function startDrag() {
  isDragging = true
  document.body.style.cursor = 'row-resize'
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(e) {
  if (!isDragging) return
  const containerHeight = window.innerHeight
  const newTop = e.clientY
  if (newTop > 100 && newTop < containerHeight - 100) {
    store.setHeights(newTop, containerHeight - newTop)
  }
}

function stopDrag() {
  isDragging = false
  document.body.style.cursor = 'default'
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

onMounted(() => {
  const containerHeight = window.innerHeight
  if (!store.topHeight || !store.bottomHeight) {
    const defaultTop = Math.floor(containerHeight * 2 / 3)
    const defaultBottom = containerHeight - defaultTop
    store.setHeights(defaultTop, defaultBottom)
  }

  window.addEventListener('resize', () => {
    const containerHeight = window.innerHeight
    store.setHeights(store.topHeight, containerHeight - store.topHeight)
  })
})
</script>

<style scoped>
#camera-page {
  display: flex;
  height: 100vh;
}

#split-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: 95px;
}

.top-pane, .bottom-pane {
  width: 100%;
  overflow: hidden;
}

.top-pane {
  display: flex;
  justify-content: center;
  align-items: center;
}

.divider {
  height: 6px;
  cursor: row-resize;
}
</style>
