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
        <tr v-for="(cam, idx) in model.cameras" :key="idx">
          <td>Камера {{ idx + 1 }}</td>
          <td>{{ cam.name }}</td>
          <td>{{ cam.kind }}</td>
          <td>{{ cam.device_id }}</td>
          <td>
            <v-checkbox
              v-if="cam.is_mobile"
              v-model="cam.scrcpy"
              :true-value="true"
              :false-value="false"
              hide-details
            />
          </td>
        </tr>

        <tr v-if="model.microphone">
          <td>Микрофон</td>
          <td>{{ model.microphone.name }}</td>
          <td>{{ model.microphone.kind }}</td>
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
      :selected-cameras="model.cameras"
      :selected-microphone="model.microphone"
      @refresh="refreshDevices"
      @confirm="applySelection"
    />
  </div>
</template>

<script setup>
import isEqual from 'lodash/isEqual'
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

function makeStubCamera() {
  return { device_id: 'stub', name: 'Нет камеры', kind: 'stub', is_stub: true }
}

function makeStubMicrophone() {
  return { device_id: 'stub', name: 'Нет микрофона', kind: 'stub', is_stub: true }
}

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

    function pickTwoCameras() {
      if (cameras.value.length === 0) {
        return [makeStubCamera(), makeStubCamera()]
      }
      if (cameras.value.length === 1) {
        return [cameras.value[0], model.value.cameras[0]]
      }
      return [cameras.value[0], cameras.value[1]]
    }

    function pickMicrophone() {
      if (microphones.value.length > 0) {
        return microphones.value[0]
      }
      return makeStubMicrophone()
    }

    if (!model.value.cameras || model.value.cameras.length === 0 ||
        (model.value.cameras.length === 1 && model.value.cameras[0].is_stub)) {
      model.value.cameras = pickTwoCameras()
    }

    if (model.value.cameras && model.value.cameras.length === 2) {
      const [cam1, cam2] = model.value.cameras
      if (cam1.is_stub && cam2.is_stub) {
        model.value.cameras = pickTwoCameras()
      } else if (cam1.is_stub && cameras.value.length > 0) {
        model.value.cameras = [cameras.value[0], cam2]
      } else if (cam2.is_stub && cameras.value.length > 1) {
        model.value.cameras = [cam1, cameras.value[1]]
      }
    }

    while (!model.value.cameras || model.value.cameras.length < 2) {
      model.value.cameras.push(makeStubCamera())
    }

    if (cameras.value.length === 1 && isEqual(model.value.cameras[0], model.value.cameras[1])) {
      model.value.cameras[1] = makeStubCamera()
    }

    if (!model.value.microphone || model.value.microphone.is_stub) {
      model.value.microphone = pickMicrophone()
    }

  } catch (err) {
    console.error("Ошибка при обновлении устройств:", err)
  }
}

function applySelection(selection) {
  if (selection.cameras) {
    model.value.cameras = selection.cameras.map(c => ({
      ...c,
      scrcpy: c.scrcpy ?? (c.is_mobile ? true : false)
    }))
  }
  if (selection.microphone) {
    model.value.microphone = selection.microphone
  }
  dialog.value = false
}

onMounted(() => {
  if (!model.value.cameras || model.value.cameras.length === 0) {
    model.value.cameras = [makeStubCamera(), makeStubCamera()]
  } else if (model.value.cameras.length === 1) {
    model.value.cameras.push(makeStubCamera())
  }

  while (model.value.cameras.length < 2) {
    model.value.cameras.push(makeStubCamera())
  }

  if (!model.value.microphone) {
    model.value.microphone = makeStubMicrophone()
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
