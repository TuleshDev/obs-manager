<template>
  <v-card title="Доступные устройства">
    <v-card-text>
      <v-btn color="secondary" class="mb-3" @click="$emit('refresh')">Обновить</v-btn>

      <h3 class="mb-2">Камеры</h3>
      <v-table>
        <thead>
          <tr><th>Имя</th><th>Тип</th></tr>
        </thead>
        <tbody>
          <tr v-for="c in cameras" :key="c.name">
            <td>{{ c.name }}</td>
            <td>{{ c.kind }}</td>
          </tr>
        </tbody>
      </v-table>

      <h3 class="mt-4 mb-2">Микрофоны</h3>
      <v-table>
        <thead>
          <tr><th>Имя</th><th>Тип</th></tr>
        </thead>
        <tbody>
          <tr v-for="m in microphones" :key="m.name">
            <td>{{ m.name }}</td>
            <td>{{ m.kind }}</td>
          </tr>
        </tbody>
      </v-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  cameras: { type: Array, default: () => [] },
  microphones: { type: Array, default: () => [] }
})
</script>
