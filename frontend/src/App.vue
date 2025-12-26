<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" permanent>
      <v-list density="compact">
        <v-list-item to="/" title="Главная" />
        <v-list-item to="/settings" title="Настройки" />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar title="OBS Manager" />

    <v-main>
      <router-view @message="showMessage($event.msg, $event.type)" />
      <v-snackbar
        v-model="show"
        location="top"
        timeout="-1"
        :color="type === 'success' ? 'green' : 'red'"
      >
        {{ message }}

        <template v-slot:actions>
          <v-btn
            v-if="type === 'error'"
            color="white"
            variant="text"
            @click="show = false"
          >
            Закрыть
          </v-btn>
        </template>
      </v-snackbar>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from './api'
import SettingsForm from './components/SettingsForm.vue'
import DeviceList from './components/DeviceList.vue'
import ActionsPanel from './components/ActionsPanel.vue'

const drawer = ref(true)

const message = ref('')
const type = ref('success')
const show = ref(false)

const showMessage = (msg, msgType = 'success') => {
  message.value = msg
  type.value = msgType
  show.value = true

  if (type.value !== 'error') {
    setTimeout(() => {
      show.value = false
    }, 3000)
  }
}
</script>

<style>
h2 { margin: 16px 0; }
</style>
