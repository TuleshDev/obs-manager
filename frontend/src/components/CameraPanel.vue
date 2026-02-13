<template>
  <v-btn
    color="primary"
    class="mt-2"
    @click="openCamera"
  >
    Открыть камеру
  </v-btn>
</template>

<script setup>
function openCamera() {
  window.open('/camera', '_blank')
}
</script>
