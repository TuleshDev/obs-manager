<template>
  <v-container>
    <h2>Главная</h2>
    <div v-if="clientStore.id">
      <p>Текущий клиент выбран: {{ clientStore.first_name }} {{ clientStore.last_name }}</p>
      <v-btn color="primary" :to="{ path: '/client' }">
        Перейти к клиенту
      </v-btn>
    </div>
    <SelectClient />
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCurrentClientStore } from '../stores/currentClient'
import SelectClient from '../components/SelectClient.vue'

const clientStore = useCurrentClientStore()

onMounted(() => {
  clientStore.loadFromStorage()
})
</script>
