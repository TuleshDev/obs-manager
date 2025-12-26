<script setup>
import { ref, onMounted } from 'vue'
import SettingsForm from '../components/SettingsForm.vue'
import ActionsPanel from '../components/ActionsPanel.vue'
import DeviceList from '../components/DeviceList.vue'
import { api } from '../api'

const tab = ref('config')

const config = ref({})
const cameras = ref([])
const microphones = ref([])

const loadConfig = async () => {
  try {
    const res = await api.getConfig()
    config.value = res
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error");
  }
}

const apply = async () => {
  try {
    const res = await api.apply()
    emitMessage("Успех: " + res.message, "success");
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error");
  }
}

const refreshDevices = async () => {
  try {
    const res = await api.listDevices()
    console.log(res.cameras)
    console.log(res.microphones)
    cameras.value = res.cameras || []
    microphones.value = res.microphones || []
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error");
  }
}

const emit = defineEmits(['message'])
function emitMessage(msg, type) {
  emit('message', { msg, type })
}

onMounted(() => {
  loadConfig()
  refreshDevices()
})
</script>

<template>
  <v-container>
    <v-tabs
      v-model="tab"
      class="mb-4"
      align-tabs="center"
    >
      <v-tab
        value="config"
        class="rounded-pill mx-2"
        color="primary"
      >
        Настройки и действия
      </v-tab>
      <v-tab
        value="devices"
        class="rounded-pill mx-2"
        color="primary"
      >
        Доступные устройства
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="tab">
      <v-tabs-window-item value="config">
        <SettingsForm
          @updated="loadConfig"
          @error="emitMessage($event, 'error')"
          :config="config"
        />
        <ActionsPanel @apply="apply" />
      </v-tabs-window-item>

      <v-tabs-window-item value="devices">
        <DeviceList
          :cameras="cameras"
          :microphones="microphones"
          @refresh="refreshDevices"
        />
      </v-tabs-window-item>
    </v-tabs-window>
  </v-container>
</template>
