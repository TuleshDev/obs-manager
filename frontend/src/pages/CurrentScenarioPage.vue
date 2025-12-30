<template>
  <v-container>
    <h2>Текущий сценарий</h2>
    <div v-if="scenarioStore.id">
      <ScenarioForm
        v-model="scenarioStore"
        @save="saveScenario"
      />
    </div>
    <div v-else>
      <p>Сценарий не выбран</p>
    </div>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import ScenarioForm from '../components/ScenarioForm.vue'
import { api } from '../api'
import { useSnackbar } from '../composables/useSnackbar'
import { useCurrentScenarioStore } from '../stores/currentScenario'

const scenarioStore = useCurrentScenarioStore()
const { showMessage } = useSnackbar()

const loadScenario = async () => {
  if (!scenarioStore.id) return
  try {
    const data = await api.getScenario(scenarioStore.id)
    scenarioStore.setScenario(data)
  } catch (err) {
    showMessage('Ошибка загрузки сценария: ' + err.message, 'error')
  }
}

const saveScenario = async (data) => {
  try {
    if (data.id) {
      await api.updateScenario(data.id, data)
      scenarioStore.setScenario(data)
      showMessage('Сценарий обновлён!')
    } else {
      const created = await api.createScenario(data)
      scenarioStore.setScenario(created)
      showMessage('Сценарий добавлен!')
    }
  } catch (err) {
    showMessage('Ошибка сохранения: ' + err.message, 'error')
  }
}

onMounted(() => {
  scenarioStore.loadFromStorage()
})
</script>
