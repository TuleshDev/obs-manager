import { defineStore } from 'pinia'

export const useCurrentScenarioStore = defineStore('currentScenario', {
  state: () => ({
    id: null,
    name: '',
    description: ''
  }),
  actions: {
    setScenario(data) {
      Object.assign(this, data)
      localStorage.setItem('currentScenario', JSON.stringify(this.$state))
    },
    clearScenario() {
      this.$reset()
      localStorage.removeItem('currentScenario')
    },
    loadFromStorage() {
      const saved = localStorage.getItem('currentScenario')
      if (saved) {
        Object.assign(this, JSON.parse(saved))
      }
    }
  }
})
