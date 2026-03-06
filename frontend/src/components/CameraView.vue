<template>
  <div class="camera-container">
    <video ref="video" autoplay playsinline></video>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useCameraLayoutStore } from '../stores/cameraLayout'

const store = useCameraLayoutStore()
const video = ref(null)
let stream = null

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.value.srcObject = stream
    console.log("Камера запущена")
  } catch (err) {
    console.error("Ошибка доступа к камере:", err)
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    video.value.srcObject = null
    stream = null
    console.log("Камера остановлена")
  }
}

onMounted(() => {
  if (store.cameraActive) {
    startCamera()
  }
})

watch(
  () => store.cameraActive,
  (active) => {
    if (active) {
      startCamera()
    } else {
      stopCamera()
    }
  }
)
</script>

<style scoped>
.camera-container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}
video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
