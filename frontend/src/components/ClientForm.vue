<template>
  <v-card>
    <v-card-title>
      {{ form.id ? 'Редактирование клиента' : 'Создание клиента' }}
    </v-card-title>
    <v-card-text>
      <v-form @submit.prevent="onSubmit">
        <v-text-field v-model="form.first_name" label="Имя" required />
        <v-text-field v-model="form.last_name" label="Фамилия" required />
        <v-text-field v-model="form.email" label="Email" required />
        <v-text-field v-model="form.city" label="Город" />
        <v-text-field v-model="form.address" label="Адрес" />
        <v-text-field v-model="form.phone" label="Телефон" />

        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field v-model="form.chapter" label="Глава" type="number" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field v-model="form.paragraph" label="Параграф" type="number" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field v-model="form.section" label="Раздел" type="number" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field v-model="form.position" label="Позиция" type="number" />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field v-model="form.task_number" label="Номер задания" type="number" />
          </v-col>
        </v-row>

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
