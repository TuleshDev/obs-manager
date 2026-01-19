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

        <v-select
          v-model="activeCameraSlot"
          :items="[0,1]"
          :item-title="slot => cameraSlots[slot]"
          :item-value="slot => slot"
          label="Выберите камеру"
          class="mb-3"
        />

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
              :class="{ 'selected-row': isSelected(index) }"
              @click="selectCamera(index)"
              :style="{ pointerEvents: isDisabled(index) ? 'none' : 'auto', opacity: isDisabled(index) ? 0.5 : 1 }"
            >
              <td>
                <v-radio
                  v-model="selectedCamerasIndices[activeCameraSlot]"
                  :value="index"
                  :disabled="isDisabled(index)"
                />
              </td>
              <td>{{ c.name }}</td>
              <td>{{ c.inputKind }}</td>
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
              <td>{{ m.inputKind }}</td>
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

function makeStubCamera() {
  return { device_id: 'stub', name: 'Нет камеры', inputKind: 'stub', is_stub: true }
}

function makeStubMicrophone() {
  return { device_id: 'stub', name: 'Нет микрофона', inputKind: 'stub', is_stub: true }
}

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  cameras: { type: Array, default: () => [] },
  microphones: { type: Array, default: () => [] },
  selectedCameras: { type: Array, default: () => [] },
  selectedMicrophone: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'confirm', 'refresh'])

const dialog = ref(props.modelValue)
watch(() => props.modelValue, val => dialog.value = val)
watch(dialog, val => emit('update:modelValue', val))

const selectedCamerasIndices = ref([null, null])
const selectedMicrophoneIndex = ref(null)

const prevCamerasIndices = ref([null, null])
const prevMicrophoneIndex = ref(null)

const activeCameraSlot = ref(0)
const cameraSlots = ["Камера 1", "Камера 2"]

function isSelected(index) {
  return selectedCamerasIndices.value[activeCameraSlot.value] === index
}

function isDisabled(index) {
  if (activeCameraSlot.value === 1 && selectedCamerasIndices.value[0] === index) {
    index === 0 ? selectedCamerasIndices.value[1] = 1 : selectedCamerasIndices.value[1] = 0
    return true
  }
  return false
}

function selectCamera(index) {
  if (!isDisabled(index)) {
    selectedCamerasIndices.value[activeCameraSlot.value] = index
  }
}

function checkSelectedCamerasIndices() {
  let idx = selectedCamerasIndices.value[1]
  if (selectedCamerasIndices.value[0] === idx) {
    idx === 0 ? selectedCamerasIndices.value[1] = 1 : selectedCamerasIndices.value[1] = 0
  }
}

function findDeviceIndex(devices, target, index = 0) {
  if (!devices || devices.length === 0 || !target) return -1
  if (target.is_stub || target.inputKind === 'stub') return index
  if (target.device_id && target.device_id !== 'unknown') {
    const byId = devices.findIndex(d => d.device_id === target.device_id)
    if (byId !== -1) return byId
  }
  if (target.inputKind) {
    const byInputKind = devices.findIndex(d => d.inputKind === target.inputKind)
    if (byInputKind !== -1) return byInputKind
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

  let cams = [...props.cameras]
  if (cams.length === 0) {
    cams = [makeStubCamera(), makeStubCamera()]
  } else if (cams.length === 1) {
    cams.push(makeStubCamera())
  }
  props.cameras.splice(0, props.cameras.length, ...cams)

  let mics = [...props.microphones]
  if (mics.length === 0) {
    mics = [makeStubMicrophone()]
  }
  props.microphones.splice(0, props.microphones.length, ...mics)

  if (props.selectedCameras && props.selectedCameras.length > 0) {
    props.selectedCameras.forEach((cam, idx) => {
      const idxCam = findDeviceIndex(props.cameras, cam, idx)
      if (idxCam !== -1) {
        selectedCamerasIndices.value[idx] = idxCam
      } else {
        if (idx === 0) {
          selectedCamerasIndices.value[0] = props.cameras.length > 0 ? 0 : null
        } else if (idx === 1) {
          selectedCamerasIndices.value[1] = props.cameras.length > 1 ? 1 : null
        }
      }
    })
  } else {
    selectedCamerasIndices.value[0] = props.cameras.length > 0 ? 0 : null
    selectedCamerasIndices.value[1] = props.cameras.length > 1 ? 1 : null
  }

  checkSelectedCamerasIndices()

  const idxMic = findDeviceIndex(props.microphones, props.selectedMicrophone)
  selectedMicrophoneIndex.value = idxMic !== -1 ? idxMic : 0

  activeCameraSlot.value = 0
}

watch(props, (val) => {
  if (dialog.value) {
    updateDevices()
  }
})

function confirmSelection() {
  checkSelectedCamerasIndices()

  const cams = selectedCamerasIndices.value.map(idx => idx !== null ? props.cameras[idx] : null)
  const mic = selectedMicrophoneIndex.value !== null ? props.microphones[selectedMicrophoneIndex.value] : null

  prevCamerasIndices.value = [...selectedCamerasIndices.value]
  prevMicrophoneIndex.value = selectedMicrophoneIndex.value

  emit('confirm', { cameras: cams, microphone: mic })
  dialog.value = false
}

function cancelSelection() {
  selectedCamerasIndices.value = [...prevCamerasIndices.value]
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
