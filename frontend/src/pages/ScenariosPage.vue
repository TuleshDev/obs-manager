<template>
  <v-container>
    <h2>Список сценариев</h2>

    <v-row class="mb-4">
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="search"
          label="Поиск"
          prepend-inner-icon="mdi-magnify"
        />
      </v-col>
      <v-col cols="12" sm="6" class="text-right">
        <v-btn color="green" @click="addScenario">
          Добавить сценарий
        </v-btn>
      </v-col>
    </v-row>

    <v-data-table
      :headers="headers"
      :items="scenarios"
      :search="search"
      :items-per-page="5"
      item-key="id"
      class="elevation-1"
    >
      <template v-slot:item.actions="{ item }">
        <v-btn
          color="blue"
          variant="text"
          @click="editScenario(item)"
        >
          Редактировать
        </v-btn>
        <v-btn
          color="red"
          variant="text"
          @click="deleteScenario(item.id)"
        >
          Удалить
        </v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <template v-slot:default>
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
          <v-card-text>
            <ScenarioForm
              v-if="selectedScenario"
              :model-value="selectedScenario"
              @save="saveScenario"
            />
          </v-card-text>
        </v-card>
      </template>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import ScenarioForm from '../components/ScenarioForm.vue'
import { useSnackbar } from '../composables/useSnackbar'

const scenarios = ref([])
const dialog = ref(false)
const selectedScenario = ref(null)
const search = ref('')

const { showMessage } = useSnackbar()

const headers = [
  { title: 'ID', key: 'id', sortable: true },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Описание', key: 'description', sortable: false },
  { title: 'Действия', key: 'actions', sortable: false }
]

const loadScenarios = async () => {
  try {
    scenarios.value = await api.listScenarios()
  } catch (err) {
    showMessage('Ошибка загрузки: ' + err.message, 'error')
  }
}

const addScenario = () => {
  selectedScenario.value = {
    name: '',
    description: ''
  }
  dialog.value = true
}

const editScenario = (scenario) => {
  selectedScenario.value = { ...scenario }
  dialog.value = true
}

const saveScenario = async (data) => {
  try {
    if (data.id) {
      await api.updateScenario(data.id, data)
      showMessage('Сценарий обновлён!')
    } else {
      await api.createScenario(data)
      showMessage('Сценарий добавлен!')
    }
    dialog.value = false
    loadScenarios()
  } catch (err) {
    showMessage('Ошибка сохранения: ' + err.message, 'error')
  }
}

const deleteScenario = async (id) => {
  if (!confirm('Удалить сценарий?')) return
  try {
    await api.deleteScenario(id)
    showMessage('Сценарий удалён!')
    loadScenarios()
  } catch (err) {
    showMessage('Ошибка удаления: ' + err.message, 'error')
  }
}

onMounted(loadScenarios)
</script>
