<template>
  <v-navigation-drawer
    app
    permanent
    width="95"
    class="control-sidebar"
  >
    <div class="sidebar-controls">
      <v-btn color="primary" size="small" block @click="resetDivider">
        <span>Сбросить</span>
      </v-btn>

      <v-btn color="primary" size="small" block @click="toggleCamera">
        <span>Пауза<br/>Запуск</span>
      </v-btn>

      <v-btn color="primary" size="small" block @click="clearEditor">
        <span>Очистить</span>
      </v-btn>

      <v-btn color="primary" size="small" block @click="exportCode">
        <span>Экспорт</span>
      </v-btn>

      <v-select
        :items="['vs-dark','vs-light']"
        v-model="store.editorTheme"
        hide-details
        class="theme-select"
        :menu-props="{ contentClass: 'theme-select-menu' }"
      ></v-select>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import { useCameraLayoutStore } from '../stores/cameraLayout'

const store = useCameraLayoutStore()

function resetDivider() {
  const containerHeight = window.innerHeight
  const defaultTop = Math.floor(containerHeight * 2 / 3)
  const defaultBottom = containerHeight - defaultTop
  store.resetHeights(defaultTop, defaultBottom)
}

function toggleCamera() {
  store.toggleCamera()
}

function clearEditor() {
  store.clearEditor()
}

function exportCode() {
  store.exportCode()
}
</script>

<style scoped>
.control-sidebar {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 4px;
}

.control-sidebar .v-btn {
  margin-bottom: 6px;
  font-size: 8px;
  padding: 6px;
}

.sidebar-controls {
  padding: 0 4px;
}

:deep(.theme-select .v-field__input) {
  min-height: 28px;
  font-size: 8px;
  padding: 0 8px;
}

:deep(.theme-select .v-field__append-inner) {
  font-size: 8px;
  width: 10px;
  min-width: 10px;
  padding: 0;
  margin-right: 2px;
}

:global(.theme-select-menu .v-list .v-list-item) {
  min-height: 24px;
  font-size: 8px;
  padding: 0 4px;
}

:global(.theme-select-menu .v-list .v-list-item-title) {
  font-size: 8px;
}
</style>
