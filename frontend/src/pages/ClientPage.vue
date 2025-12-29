<template>
  <v-container>
    <h2>Текущий клиент</h2>
    <div v-if="clientStore.id">
      <ClientForm
        v-model="clientStore"
        @save="saveClient"
      />
    </div>
    <div v-else>
      <p>Клиент не выбран</p>
    </div>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import ClientForm from '../components/ClientForm.vue'
import { api } from '../api'
import { useSnackbar } from '../composables/useSnackbar'
import { useCurrentClientStore } from '../stores/currentClient'

const clientStore = useCurrentClientStore()
const { showMessage } = useSnackbar()

const loadClient = async () => {
  if (!clientStore.id) return
  try {
    const data = await api.getStudent(clientStore.id)
    clientStore.setClient(data)
  } catch (err) {
    showMessage('Ошибка загрузки клиента: ' + err.message, 'error')
  }
}

const saveClient = async (data) => {
  try {
    if (data.id) {
      await api.updateStudent(data.id, data)
      clientStore.setClient(data)
      showMessage('Клиент обновлён!')
    } else {
      const created = await api.createStudent(data)
      clientStore.setClient(created)
      showMessage('Клиент добавлен!')
    }
  } catch (err) {
    showMessage('Ошибка сохранения: ' + err.message, 'error')
  }
}

onMounted(() => {
  clientStore.loadFromStorage()
})
</script>
