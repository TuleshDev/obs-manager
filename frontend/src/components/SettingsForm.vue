<template>
  <v-card class="mb-6" title="Настройки">
    <v-card-text>
      <v-form @submit.prevent="save">
        <v-text-field v-model="local.ws_host" label="WS Host" />
        <v-text-field v-model="local.ws_port" label="WS Port" type="number" />

        <v-switch v-model="local.allow_delete_scenes" label="Разрешить удаление сцен" />

        <v-text-field v-model="local.main_scene_name" label="Имя основной сцены" />
        <v-text-field v-model="local.camera_source_name" label="Имя источника камеры" />

        <v-select
          v-model="local.camera_input_kind"
          :items="['dshow_input','v4l2_input','av_capture_input']"
          label="Тип устройства камеры"
        />

        <v-text-field v-model="local.camera_device_id" label="Device ID" />

        <v-btn type="submit" color="primary" class="mt-4">Сохранить</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { reactive, watch, toRaw } from 'vue'
import { api } from '../api'

const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['updated', 'error'])

const local = reactive({
  ws_host: '',
  ws_port: 4455,
  allow_delete_scenes: false,
  main_scene_name: 'MainScene',
  camera_source_name: 'MyCamera',
  camera_input_kind: 'dshow_input',
  camera_device_id: 'default',
})

watch(() => props.config, (cfg) => Object.assign(local, cfg || {}), { immediate: true })

const save = async () => {
  try {
    await api.updateConfig(toRaw(local))
    emit('updated')
  } catch (err) {
    emit('error', "Ошибка: " + err.message);
  }
}
</script>
