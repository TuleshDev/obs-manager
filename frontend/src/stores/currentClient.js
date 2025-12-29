import { defineStore } from 'pinia'

export const useCurrentClientStore = defineStore('currentClient', {
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
    task_number: 0
  }),
  actions: {
    setClient(data) {
      Object.assign(this, data)
      localStorage.setItem('currentClient', JSON.stringify(this.$state))
    },
    clearClient() {
      this.$reset()
      localStorage.removeItem('currentClient')
    },
    loadFromStorage() {
      const saved = localStorage.getItem('currentClient')
      if (saved) {
        Object.assign(this, JSON.parse(saved))
      }
    }
  }
})
