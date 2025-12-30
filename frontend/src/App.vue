<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" permanent>
      <v-list density="compact">
        <v-list-item to="/" title="Главная" />
        <v-list-item to="/currentstudent">
          {{ studentStore.id ? 'Текущий студент: ' + studentStore.first_name : 'Студент' }}
        </v-list-item>
        <v-list-item to="/students" title="Все студенты" />
        <v-list-item to="/currentscenario">
          {{ scenarioStore.id ? 'Текущий сценарий: ' + scenarioStore.name : 'Сценарий' }}
        </v-list-item>
        <v-list-item to="/scenarios" title="Все сценарии" />
        <v-list-item to="/settings" title="Настройки" />
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
import { useCurrentScenarioStore } from './stores/currentScenario'
import { useCurrentStudentStore } from './stores/currentStudent'
import Snackbar from './components/Snackbar.vue'
import { useSnackbar } from './composables/useSnackbar'

const drawer = ref(true)

const scenarioStore = useCurrentScenarioStore()
const studentStore = useCurrentStudentStore()

const { showMessage } = useSnackbar()

onMounted(() => {
  scenarioStore.loadFromStorage()
  studentStore.loadFromStorage()
})
</script>

<style>
h2 { margin: 16px 0; }
</style>
