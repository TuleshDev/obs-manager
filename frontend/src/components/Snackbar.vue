<template>
  <v-snackbar
    v-model="show"
    location="top"
    timeout="-1"
    :color="colors[type]"
  >
    <v-row align="center" no-gutters>
      <v-col cols="auto">
        <v-icon>{{ icons[type] }}</v-icon>
      </v-col>
      <v-col>
        {{ message }}
      </v-col>
    </v-row>

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
</template>

<script setup>
import { useSnackbar } from '../composables/useSnackbar'

const { message, type, show } = useSnackbar()

const colors = {
  success: 'green',
  error: 'red',
  warning: 'orange',
  info: 'blue'
}

const icons = {
  success: 'mdi-check-circle',
  error: 'mdi-alert-circle',
  warning: 'mdi-alert',
  info: 'mdi-information'
}
</script>

<style>
.v-snackbar .v-icon { margin-right: 8px; }
</style>
