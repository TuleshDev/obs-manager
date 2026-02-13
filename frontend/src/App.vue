<template>
  <v-app>
    <router-view @message="showMessage($event.msg, $event.type)" />
    <Snackbar />
  </v-app>
</template>

<script setup>
import Snackbar from './components/Snackbar.vue'
import { useSnackbar } from './composables/useSnackbar'

const { showMessage } = useSnackbar()
</script>

<style>
h2 { margin: 16px 0; }
</style>
