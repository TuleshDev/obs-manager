<template>
  <v-container>
    <div v-if="scenarioStore.id">
      <v-tabs
        v-model="tab"
        class="mb-4"
        align-tabs="center"
      >
        <v-tab
          value="config"
          class="rounded-0 mx-2"
          color="primary"
        >
          Настройки
        </v-tab>
        <v-tab
          value="devices"
          class="rounded-0 mx-2"
          color="primary"
        >
          Доступные устройства
        </v-tab>
        <v-tab
          value="actions"
          class="rounded-0 mx-2"
          color="primary"
        >
          Действия
        </v-tab>
      </v-tabs>

      <v-tabs-window v-model="tab">
        <v-tabs-window-item value="config">
          <SettingsForm
            @updated="loadConfig"
            @error="emitMessage($event, 'error')"
            :global-config="config.global"
            :scenario-config="config.scenario"
          />
        </v-tabs-window-item>

        <v-tabs-window-item value="devices">
          <component
            :is="scenarioDeviceList"
            :cameras="cameras"
            :microphones="microphones"
            @refresh="refreshDevices"
          />
        </v-tabs-window-item>

        <v-tabs-window-item value="actions">
          <component
            :is="scenarioActionsPanel"
            @apply="apply"
            @downloadBackup="downloadBackup"
          />
        </v-tabs-window-item>
      </v-tabs-window>
    </div>
    <div v-else>
      <h2>Настройки</h2>
      <p>Сценарий не выбран</p>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../api'
import SettingsForm from '../components/SettingsForm.vue'
import { useCurrentScenarioStore } from '../stores/currentScenario'

import ActionsPanelMath from '../scenarios/Math/components/ActionsPanel.vue'
import ActionsPanelStreaming from '../scenarios/Streaming/components/ActionsPanel.vue'

import DeviceListMath from '../scenarios/Math/components/DeviceList.vue'
import DeviceListStreaming from '../scenarios/Streaming/components/DeviceList.vue'

const tab = ref('config')
const scenarioStore = useCurrentScenarioStore()

const config = ref({ global: {}, scenario: {} })
const cameras = ref([])
const microphones = ref([])

const scenarioActionsPanel = computed(() => {
  switch (scenarioStore.name) {
    case 'Math':
      return ActionsPanelMath
    case 'Streaming':
      return ActionsPanelStreaming
    default:
      return ActionsPanelMath
  }
})

const scenarioDeviceList = computed(() => {
  switch (scenarioStore.name) {
    case 'Math':
      return DeviceListMath
    case 'Streaming':
      return DeviceListStreaming
    default:
      return DeviceListMath
  }
})

const loadConfig = async () => {
  try {
    const res = await api.getConfig(scenarioStore.name)
    config.value = res
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error")
  }
}

const refreshDevices = async () => {
  try {
    const res = await api.listDevices()
    cameras.value = res.cameras || []
    microphones.value = res.microphones || []
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error")
  }
}

const apply = async () => {
  try {
    const backupFilename = `backup_${new Date().toISOString().replace(/[:.]/g, "-")}.json`
    await api.updateConfig({
      global: config.value.global,
      scenario_name: scenarioStore.name,
      scenario: config.value.scenario,
      backup_filename: backupFilename
    })

    const res = await api.apply({
      global: config.value.global,
      scenario_name: scenarioStore.name,
      scenario: config.value.scenario
    })

    emitMessage("Успех: " + res.message, "success")
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error")
  }
}

const downloadBackup = async () => {
  try {
    const res = await api.restoreBackup(scenarioStore.name)
    emitMessage("Успех: " + res.message, "success")

    const currentTab = tab.value
    await loadConfig()
    tab.value = currentTab
  } catch (err) {
    emitMessage("Ошибка: " + err.message, "error")
  }
}

const emit = defineEmits(['message'])
function emitMessage(msg, type) {
  emit('message', { msg, type })
}

onMounted(() => {
  scenarioStore.loadFromStorage()
  loadConfig()
  refreshDevices()
})
</script>
