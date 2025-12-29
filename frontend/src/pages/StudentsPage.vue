<template>
  <v-container>
    <h2>Список студентов</h2>

    <v-row class="mb-4">
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="search"
          label="Поиск"
          prepend-inner-icon="mdi-magnify"
        />
      </v-col>
      <v-col cols="12" sm="6" class="text-right">
        <v-btn color="green" @click="addStudent">
          Добавить студента
        </v-btn>
      </v-col>
    </v-row>

    <v-data-table
      :headers="headers"
      :items="students"
      :search="search"
      :items-per-page="5"
      item-key="id"
      class="elevation-1"
    >
      <template v-slot:item.actions="{ item }">
        <v-btn
          color="blue"
          variant="text"
          @click="editStudent(item)"
        >
          Редактировать
        </v-btn>
        <v-btn
          color="red"
          variant="text"
          @click="deleteStudent(item.id)"
        >
          Удалить
        </v-btn>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <template v-slot:default>
        <v-btn
          icon
          size="x-small"
          class="position-absolute"
          style="top: -20px; right: -20px; z-index: 2000; width: 24px; height: 24px;"
          @click="dialog = false"
        >
          <v-icon size="16">mdi-close</v-icon>
        </v-btn>

        <v-card>
          <v-card-text>
            <ClientForm
              v-if="selectedStudent"
              :model-value="selectedStudent"
              @save="saveStudent"
            />
          </v-card-text>
        </v-card>
      </template>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
import ClientForm from '../components/ClientForm.vue'
import { useSnackbar } from '../composables/useSnackbar'

const students = ref([])
const dialog = ref(false)
const selectedStudent = ref(null)
const search = ref('')

const { showMessage } = useSnackbar()

const headers = [
  { title: 'ID', key: 'id', sortable: true },
  { title: 'Имя', key: 'first_name', sortable: true },
  { title: 'Фамилия', key: 'last_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Город', key: 'city', sortable: true },
  { title: 'Адрес', key: 'address', sortable: false },
  { title: 'Телефон', key: 'phone', sortable: false },
  { title: 'Действия', key: 'actions', sortable: false }
]

const loadStudents = async () => {
  try {
    students.value = await api.listStudents()
  } catch (err) {
    showMessage('Ошибка загрузки: ' + err.message, 'error')
  }
}

const addStudent = () => {
  selectedStudent.value = {
    first_name: '',
    last_name: '',
    email: '',
    city: '',
    address: '',
    phone: '',
    chapter: 0,
    paragraph: 0,
    section: 0,
    position: 0,
    task_number: 0
  }
  dialog.value = true
}

const editStudent = (student) => {
  selectedStudent.value = { ...student }
  dialog.value = true
}

const saveStudent = async (data) => {
  try {
    if (data.id) {
      await api.updateStudent(data.id, data)
      showMessage('Студент обновлён!')
    } else {
      await api.createStudent(data)
      showMessage('Студент добавлен!')
    }
    dialog.value = false
    loadStudents()
  } catch (err) {
    showMessage('Ошибка сохранения: ' + err.message, 'error')
  }
}

const deleteStudent = async (id) => {
  if (!confirm('Удалить студента?')) return
  try {
    await api.deleteStudent(id)
    showMessage('Студент удалён!')
    loadStudents()
  } catch (err) {
    showMessage('Ошибка удаления: ' + err.message, 'error')
  }
}

onMounted(loadStudents)
</script>
