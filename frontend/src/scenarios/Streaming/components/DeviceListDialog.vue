<template>
  <v-dialog v-model="dialog" max-width="800">
    <v-btn
      icon
      size="x-small"
      class="position-absolute"
      style="top: -20px; right: -20px; z-index: 2000; width: 24px; height: 24px;"
      @click="dialog = false"
    >
      <v-icon size="16">mdi-close</v-icon>
    </v-btn>

    <v-card>
      <v-card-title>Доступные устройства</v-card-title>
      <v-card-text>
        <v-btn color="secondary" class="mb-3" @click="$emit('refresh')">
          Обновить
        </v-btn>

        <h3 class="mb-2">Камеры</h3>
        <v-table class="device-table">
          <thead>
            <tr>
              <th class="col-radio"></th>
              <th class="col-name">Имя</th>
              <th class="col-kind">Тип</th>
              <th class="col-id">Device ID</th>
              <th class="col-scrcpy">scrcpy</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(c, index) in cameras"
              :key="index"
              :class="{ 'selected-row': selectedCameraIndex === index }"
              @click="selectedCameraIndex = index"
            >
              <td>
                <v-radio
                  v-model="selectedCameraIndex"
                  name="camera"
                  :value="index"
                />
              </td>
              <td>{{ c.name }}</td>
              <td>{{ c.kind }}</td>
              <td>{{ c.device_id }}</td>
              <td>
                <v-checkbox
                  v-if="c.is_mobile"
                  v-model="c.scrcpy"
                  :true-value="true"
                  :false-value="false"
                  hide-details
                />
              </td>
            </tr>
          </tbody>
        </v-table>

        <h3 class="mt-4 mb-2">Микрофоны</h3>
        <v-table class="device-table">
          <thead>
            <tr>
              <th class="col-radio"></th>
              <th class="col-name">Имя</th>
              <th class="col-kind">Тип</th>
              <th class="col-id">Device ID</th>
              <th class="col-scrcpy"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(m, index) in microphones"
              :key="index"
              :class="{ 'selected-row': selectedMicrophoneIndex === index }"
              @click="selectedMicrophoneIndex = index"
            >
              <td>
                <v-radio v-model="selectedMicrophoneIndex" name="microphone" :value="index" />
              </td>
              <td>{{ m.name }}</td>
              <td>{{ m.kind }}</td>
              <td>{{ m.device_id }}</td>
              <td></td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="confirmSelection">Подтвердить</v-btn>
        <v-btn color="error" @click="cancelSelection">Отмена</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  cameras: { type: Array, default: () => [] },
  microphones: { type: Array, default: () => [] },
  selectedCamera: { type: Object, default: null },
  selectedMicrophone: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'confirm', 'refresh'])

const dialog = ref(props.modelValue)
watch(() => props.modelValue, val => dialog.value = val)
watch(dialog, val => emit('update:modelValue', val))

const selectedCameraIndex = ref(null)
const selectedMicrophoneIndex = ref(null)

const prevCameraIndex = ref(null)
const prevMicrophoneIndex = ref(null)

function findDeviceIndex(devices, target, index = 0) {
  if (!devices || devices.length === 0 || !target) return -1
  if (target.is_stub || target.kind === 'stub') return index
  if (target.device_id && target.device_id !== 'unknown') {
    const byId = devices.findIndex(d => d.device_id === target.device_id)
    if (byId !== -1) return byId
  }
  if (target.kind) {
    const byKind = devices.findIndex(d => d.kind === target.kind)
    if (byKind !== -1) return byKind
  }
  if (target.name) {
    const byName = devices.findIndex(d => d.name === target.name)
    if (byName !== -1) return byName
  }
  return -1
}

function updateDevices() {
  props.cameras.forEach(c => {
    if (c.is_mobile && c.scrcpy === undefined) {
      c.scrcpy = true
    }
  })

  const idxCam = findDeviceIndex(props.cameras, props.selectedCamera)
  selectedCameraIndex.value = idxCam !== -1 ? idxCam : 0

  const idxMic = findDeviceIndex(props.microphones, props.selectedMicrophone)
  selectedMicrophoneIndex.value = idxMic !== -1 ? idxMic : 0
}

watch(props, (val) => {
  if (dialog.value) {
    updateDevices()
  }
})

function confirmSelection() {
  const cam = selectedCameraIndex.value !== null ? props.cameras[selectedCameraIndex.value] : null
  const mic = selectedMicrophoneIndex.value !== null ? props.microphones[selectedMicrophoneIndex.value] : null

  prevCameraIndex.value = selectedCameraIndex.value
  prevMicrophoneIndex.value = selectedMicrophoneIndex.value

  emit('confirm', { camera: cam, microphone: mic })
  dialog.value = false
}

function cancelSelection() {
  selectedCameraIndex.value = prevCameraIndex.value
  selectedMicrophoneIndex.value = prevMicrophoneIndex.value
  dialog.value = false
}
</script>

<style scoped>
.device-table {
  width: 100%;
  table-layout: fixed;
}

.col-radio {
  width: 50px;
}
.col-name {
  width: 200px;
}
.col-kind {
  width: 150px;
}
.col-id {
  width: 250px;
}
.col-scrcpy {
  width: 100px;
}

.device-table td,
.device-table th {
  white-space: normal;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.selected-row {
  background-color: #e3f2fd;
}
</style>
