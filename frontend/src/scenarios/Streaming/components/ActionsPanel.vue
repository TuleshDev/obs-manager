<template>
  <v-card class="mb-6" title="Действия">
    <v-card-text>
      <v-btn color="error" class="mr-4" @click="$emit('apply')">
        Очистить сцены, создать основную сцену и добавить камеру
      </v-btn>

      <v-btn color="primary" @click="$emit('downloadBackup')">
        Скачать последний бэкап
      </v-btn>
    </v-card-text>
  </v-card>
</template>

<script setup>
</script>
