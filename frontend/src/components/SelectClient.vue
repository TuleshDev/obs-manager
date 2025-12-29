<template>
  <div>
    <div v-if="!clientStore.id">
      <h3>Выберите клиента</h3>
      <v-btn
        v-for="student in students"
        :key="student.id"
        class="ma-2"
        @click="select(student)"
      >
        {{ student.first_name }} {{ student.last_name }}
      </v-btn>
    </div>
    <div v-else>
      <div class="mt-4">
        <v-btn color="red" @click="clear">
          Очистить выбор
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useCurrentClientStore } from '../stores/currentClient'

const students = ref([])
const clientStore = useCurrentClientStore()
const router = useRouter()

const loadStudents = async () => {
  students.value = await api.listStudents()
}

const select = (student) => {
  clientStore.setClient({
    id: student.id,
    first_name: student.first_name,
    last_name: student.last_name,
    email: student.email,
    city: student.city,
    address: student.address,
    phone: student.phone,
    chapter: student.chapter,
    paragraph: student.paragraph,
    section: student.section,
    position: student.position,
    task_number: student.task_number
  })
  router.push('/client')
}

const clear = () => {
  clientStore.clearClient()
  router.push('/')
}

onMounted(loadStudents)
</script>
