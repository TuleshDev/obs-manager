<template>
  <div>
    <div v-if="scenarioStore.id">
      <p>Текущий сценарий: {{ scenarioStore.name }}</p>
      <v-btn color="primary" :to="{ path: '/currentscenario' }">
        Перейти к сценарию
      </v-btn>
      <v-btn color="red" class="ma-2" @click="clearScenario">
        Очистить выбор
      </v-btn>
    </div>
    <div v-else>
      <div v-if="scenarios.length > 0">
        <h3>Выберите сценарий</h3>
        <v-select
          v-model="selectedScenario"
          :items="scenarios"
          item-title="name"
          item-value="id"
          label="Сценарий"
          outlined
          class="ma-2"
          @update:modelValue="selectScenario"
        />
      </div>
      <div v-else>
        <p>Нет доступных сценариев</p>
      </div>
    </div>

    <div v-if="studentStore.id">
      <p>Текущий студент: {{ studentStore.first_name }} {{ studentStore.last_name }}</p>
      <v-btn color="primary" :to="{ path: '/currentstudent' }">
        Перейти к студенту
      </v-btn>
      <v-btn color="red" class="ma-2" @click="clearStudent">
        Очистить выбор
      </v-btn>
    </div>
    <div v-else>
      <div v-if="students.length > 0">
        <h3>Выберите студента</h3>
        <v-btn
          v-for="student in students"
          :key="student.id"
          class="ma-2"
          @click="selectStudent(student)"
        >
          {{ student.first_name }} {{ student.last_name }}
        </v-btn>
      </div>
      <div v-else>
        <p>Нет доступных студентов</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { useCurrentStudentStore } from '../stores/currentStudent'
import { useCurrentScenarioStore } from '../stores/currentScenario'

const students = ref([])
const scenarios = ref([])
const selectedScenario = ref(null)

const studentStore = useCurrentStudentStore()
const scenarioStore = useCurrentScenarioStore()
const router = useRouter()

const loadData = async () => {
  students.value = await api.listStudents()
  scenarios.value = await api.listScenarios()
}

const selectScenario = async (scenarioId) => {
  const scenario = scenarios.value.find(s => s.id === scenarioId)
  if (scenario) {
    scenarioStore.setScenario(scenario)

    if (studentStore.id) {
      await api.assignScenario(studentStore.id, scenario.id)
    }
  }
}

const selectStudent = async (student) => {
  studentStore.setStudent(student)

  if (scenarioStore.id) {
    await api.assignScenario(student.id, scenarioStore.id)
  }

  router.push('/currentstudent')
}

const clearScenario = () => {
  scenarioStore.clearScenario()
  selectedScenario.value = null
}

const clearStudent = () => {
  studentStore.clearStudent()
}

onMounted(loadData)
</script>
