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
          :cameras="cameras"
          :microphones="microphones"
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
  scenarioConfig: { type: Object, default: () => ({}) },
  cameras: { type: Array, default: () => [] },
  microphones: { type: Array, default: () => [] }
})

const emit = defineEmits(['updated', 'error', 'changed', 'saved'])

const scenarioStore = useCurrentScenarioStore()

const local = reactive({
  global: {
    ws_host: '',
    ws_port: 4455
  },
  scenario: {
    allow_delete_scenes: false
  }
})

const original = reactive({
  global: {},
  scenario: {}
})

watch(
  () => props.globalConfig,
  (cfg) => {
    Object.assign(local.global, cfg || {})
    Object.assign(original.global, cfg || {})
    emit('saved')
  },
  { immediate: true }
)

watch(
  () => props.scenarioConfig,
  (cfg) => {
    Object.assign(local.scenario, cfg || {})
    Object.assign(original.scenario, cfg || {})
    emit('saved')
  },
  { immediate: true }
)

watch(local, () => {
  const changed =
    JSON.stringify(local.global) !== JSON.stringify(original.global) ||
    JSON.stringify(local.scenario) !== JSON.stringify(original.scenario)

  if (changed) emit('changed')
  else emit('saved')
}, { deep: true })

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
    Object.assign(original.global, toRaw(local.global))
    Object.assign(original.scenario, toRaw(local.scenario))
    emit('updated')
    emit('saved')
  } catch (err) {
    emit('error', 'Ошибка: ' + err.message)
  }
}
</script>
