import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import SettingsPage from './pages/SettingsPage.vue'
import ClientPage from './pages/ClientPage.vue'
import StudentsPage from './pages/StudentsPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/settings', name: 'settings', component: SettingsPage },
    { path: '/client', name: 'client', component: ClientPage },
    { path: '/students', name: 'students', component: StudentsPage }
  ]
})
