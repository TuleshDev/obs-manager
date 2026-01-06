<template>
  <v-card class="mb-6" title="Настройки">
    <v-card-text>
      <v-form @submit.prevent="save">
        <h3 class="my-4">Глобальные настройки</h3>
        <v-text-field v-model="local.global.ws_host" label="WS Host" />
        <v-text-field v-model="local.global.ws_port" label="WS Port" type="number" />

        <h3 class="mt-4 mb-2">Настройки сценария</h3>
        <component
          :is="scenarioComponent"
          v-model="local.scenario"
        />

        <v-btn type="submit" color="primary" class="mt-4">Сохранить</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { reactive, watch, toRaw, computed } from 'vue'
import { api } from '../api'
import { useCurrentScenarioStore } from '../stores/currentScenario'

import SettingsMath from '../scenarios/Math/components/Settings.vue'
import SettingsStreaming from '../scenarios/Streaming/components/Settings.vue'

const props = defineProps({
  globalConfig: { type: Object, default: () => ({}) },
  scenarioConfig: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['updated', 'error'])

const scenarioStore = useCurrentScenarioStore()

const local = reactive({
  global: {
    ws_host: '',
    ws_port: 4455
  },
  scenario: {
    allow_delete_scenes: false,
    main_scene_name: 'MainScene',
    camera_source_name: 'MyCamera',
    camera_input_kind: 'dshow_input',
    camera_device_id: 'default'
  }
})

watch(
  () => props.globalConfig,
  (cfg) => Object.assign(local.global, cfg || {}),
  { immediate: true }
)

watch(
  () => props.scenarioConfig,
  (cfg) => Object.assign(local.scenario, cfg || {}),
  { immediate: true }
)

const scenarioComponent = computed(() => {
  switch (scenarioStore.name) {
    case 'Math':
      return SettingsMath
    case 'Streaming':
      return SettingsStreaming
    default:
      return SettingsMath
  }
})

const save = async () => {
  try {
    await api.updateConfig({
      global: toRaw(local.global),
      scenario_name: scenarioStore.name,
      scenario: toRaw(local.scenario)
    })
    emit('updated')
  } catch (err) {
    emit('error', 'Ошибка: ' + err.message)
  }
}
</script>
