<template>
  <v-container>
    <h2>Текущий студент</h2>
    <div v-if="studentStore.id">
      <StudentForm
        v-model="studentStore"
        @save="saveStudent"
      />
    </div>
    <div v-else>
      <p>Студент не выбран</p>
    </div>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue'
import StudentForm from '../components/StudentForm.vue'
import { api } from '../api'
import { useSnackbar } from '../composables/useSnackbar'
import { useCurrentStudentStore } from '../stores/currentStudent'

const studentStore = useCurrentStudentStore()
const { showMessage } = useSnackbar()

const loadStudent = async () => {
  if (!studentStore.id) return
  try {
    const data = await api.getStudent(studentStore.id)
    studentStore.setStudent(data)
  } catch (err) {
    showMessage('Ошибка загрузки студента: ' + err.message, 'error')
  }
}

const saveStudent = async (data) => {
  try {
    if (data.id) {
      await api.updateStudent(data.id, data)
      studentStore.setStudent(data)
      showMessage('Студент обновлён!')
    } else {
      const created = await api.createStudent(data)
      studentStore.setStudent(created)
      showMessage('Студент добавлен!')
    }
  } catch (err) {
    showMessage('Ошибка сохранения: ' + err.message, 'error')
  }
}

onMounted(() => {
  studentStore.loadFromStorage()
})
</script>
