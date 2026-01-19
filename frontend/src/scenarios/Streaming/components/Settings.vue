<template>
  <div>
    <v-switch v-model="model.allow_delete_scenes" label="Разрешить удаление сцен" />

    <v-table class="device-table mt-4">
      <thead>
        <tr>
          <th class="col-device">Устройство</th>
          <th class="col-name">Имя</th>
          <th class="col-kind">Тип</th>
          <th class="col-id">Device ID</th>
          <th class="col-scrcpy">scrcpy</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="model.camera">
          <td>Камера</td>
          <td>{{ model.camera.name }}</td>
          <td>{{ model.camera.inputKind }}</td>
          <td>{{ model.camera.device_id }}</td>
          <td>
            <v-checkbox
              v-if="model.camera.is_mobile"
              v-model="model.camera.scrcpy"
              :true-value="true"
              :false-value="false"
              hide-details
            />
          </td>
        </tr>

        <tr v-if="model.microphone">
          <td>Микрофон</td>
          <td>{{ model.microphone.name }}</td>
          <td>{{ model.microphone.inputKind }}</td>
          <td>{{ model.microphone.device_id }}</td>
          <td></td>
        </tr>
      </tbody>
    </v-table>

    <v-btn color="primary" class="mt-4" @click="dialog = true">
      Выбрать устройства
    </v-btn>

    <DeviceListDialog
      v-model="dialog"
      :cameras="cameras"
      :microphones="microphones"
      :selected-camera="model.camera"
      :selected-microphone="model.microphone"
      @refresh="refreshDevices"
      @confirm="applySelection"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import DeviceListDialog from './DeviceListDialog.vue'
import { api } from '../../../api'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
  cameras: { type: Array, default: () => [] },
  microphones: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialog = ref(false)
const cameras = ref(props.cameras)
const microphones = ref(props.microphones)

async function refreshDevices() {
  try {
    const res = await api.listDevices()
    cameras.value = res.cameras || []
    microphones.value = res.microphones || []

    cameras.value.forEach(c => {
      if (c.is_mobile && c.scrcpy === undefined) {
        c.scrcpy = true
      } else {
        c.scrcpy = false
      }
    })

    if ((!model.value.camera || model.value.camera.is_stub) && cameras.value.length > 0) {
      model.value.camera = cameras.value[0]
    }
    if ((!model.value.microphone || model.value.microphone.is_stub) && microphones.value.length > 0) {
      model.value.microphone = microphones.value[0]
    }
  } catch (err) {
    console.error("Ошибка при обновлении устройств:", err)
  }
}

function applySelection(selection) {
  if (selection.camera) {
    model.value.camera = {
      ...selection.camera,
      scrcpy: selection.camera.scrcpy ?? (selection.camera.is_mobile ? true : false)
    }
  }
  if (selection.microphone) {
    model.value.microphone = selection.microphone
  }
  dialog.value = false
}

onMounted(() => {
  if (!model.value.camera) {
    model.value.camera = { device_id: 'stub', name: 'Нет камеры', inputKind: 'stub', is_stub: true }
  }
  if (!model.value.microphone) {
    model.value.microphone = { device_id: 'stub', name: 'Нет микрофона', inputKind: 'stub', is_stub: true }
  }

  refreshDevices()
})
</script>

<style scoped>
.device-table {
  width: 100%;
  table-layout: fixed;
}

.col-device {
  width: 120px;
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
</style>
