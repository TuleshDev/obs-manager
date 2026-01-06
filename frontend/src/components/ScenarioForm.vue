<template>
  <v-card>
    <v-card-title>
      {{ form.id ? 'Редактирование сценария' : 'Создание сценария' }}
    </v-card-title>
    <v-card-text>
      <v-form @submit.prevent="onSubmit">
        <v-text-field
          v-model="form.name"
          label="Название сценария"
          required
          :disabled="!!form.id"
        />
        <v-textarea
          v-model="form.description"
          label="Описание"
          required
          rows="10"
        />

        <v-btn type="submit" color="primary" class="mt-4">Сохранить</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['update:modelValue', 'save'])

const form = reactive({ ...props.modelValue })

const onSubmit = () => {
  emit('save', { ...form })
}
</script>
