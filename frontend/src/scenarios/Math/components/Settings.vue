<template>
  <div>
    <v-switch v-model="model.allow_delete_scenes" label="Разрешить удаление сцен" />

    <v-text-field v-model="model.main_scene_name" label="Имя основной сцены" />
    <v-text-field v-model="model.camera_source_name" label="Имя источника камеры" />

    <v-select
      v-model="model.camera_input_kind"
      :items="['dshow_input','v4l2_input','av_capture_input']"
      label="Тип устройства камеры"
    />

    <v-text-field v-model="model.camera_device_id" label="Device ID" />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>
