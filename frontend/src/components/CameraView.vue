<template>
  <div class="camera-container">
    <video ref="video" autoplay playsinline></video>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useSnackbar } from '../composables/useSnackbar'

const { showMessage } = useSnackbar()
const video = ref(null)

onMounted(async () => {
  try {
    // const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
	const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.value.srcObject = stream
    showMessage("Успех: камера успешно запущена")
  } catch (err) {
    console.error("Ошибка доступа к камере:", err)
    showMessage("Ошибка: доступ к камере невозможен", "error")
  }
})
</script>

<style scoped>
.camera-container {
  width: 100vw;
  height: 100vh;
  background: black;
  margin: 0;
  padding: 0;
}
video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
