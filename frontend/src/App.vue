<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" permanent>
      <v-list density="compact">
        <v-list-item to="/" title="Главная" />
        <v-list-item to="/settings" title="Настройки" />
        <v-list-item to="/client" title="Клиент" />
        <v-list-item to="/students" title="Студенты" />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar title="OBS Manager" />

    <v-main>
      <router-view @message="showMessage($event.msg, $event.type)" />
      <Snackbar />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from './api'
import Snackbar from './components/Snackbar.vue'
import { useSnackbar } from './composables/useSnackbar'

const drawer = ref(true)

const { showMessage } = useSnackbar()
</script>

<style>
h2 { margin: 16px 0; }
</style>
