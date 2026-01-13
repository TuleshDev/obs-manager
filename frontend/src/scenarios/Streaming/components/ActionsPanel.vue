<template>
  <v-card class="mb-6" title="Действия">
    <v-card-text>
      <div class="d-flex flex-wrap align-center">
        <v-card class="pa-3 mr-4 mb-4">
          <v-switch v-model="useTemplate" label="Использовать шаблон" />
          <v-btn color="error" @click="handleExportTo">
            Перенастроить Obs Studio
          </v-btn>
        </v-card>

        <v-btn color="primary" class="mr-4 mb-4" @click="$emit('downloadBackup')">
          Скачать последний бэкап
        </v-btn>

        <v-btn color="success" class="mb-4" @click="$emit('importFrom')">
          Получить настройки от Obs Studio
        </v-btn>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from "vue"

const emit = defineEmits(["exportTo", "downloadBackup", "importFrom"])

const useTemplate = ref(false)

const handleExportTo = () => {
  emit("exportTo", { useTemplate: useTemplate.value })

  useTemplate.value = false
}
</script>
