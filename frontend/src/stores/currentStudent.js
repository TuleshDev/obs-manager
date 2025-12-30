import { defineStore } from 'pinia'
import { useCurrentScenarioStore } from './currentScenario'

export const useCurrentStudentStore = defineStore('currentStudent', {
  state: () => ({
    id: null,
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
    task_number: 0,
    scenario_id: null
  }),
  actions: {
    async setStudent(data) {
      Object.assign(this, data)
      localStorage.setItem('currentStudent', JSON.stringify(this.$state))

      if (data.scenario_id) {
        const scenarioStore = useCurrentScenarioStore()
        try {
          const response = await fetch(`/api/scenarios/${data.scenario_id}`)
          if (response.ok) {
            const scenario = await response.json()
            scenarioStore.setScenario(scenario)
          } else {
            scenarioStore.clearScenario()
          }
        } catch (err) {
          console.error("Ошибка загрузки сценария:", err)
          scenarioStore.clearScenario()
        }
      }
    },
    clearStudent() {
      this.$reset()
      localStorage.removeItem('currentStudent')

      // const scenarioStore = useCurrentScenarioStore()
      // scenarioStore.clearScenario()
    },
    loadFromStorage() {
      const saved = localStorage.getItem('currentStudent')
      if (saved) {
        Object.assign(this, JSON.parse(saved))
      }
    }
  }
})
