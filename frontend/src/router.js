import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from './layouts/MainLayout.vue'
import HomePage from './pages/HomePage.vue'
import CameraLayout from './layouts/CameraLayout.vue'
import CameraPage from './pages/CameraPage.vue'
import SettingsPage from './pages/SettingsPage.vue'
import CurrentStudentPage from './pages/CurrentStudentPage.vue'
import StudentsPage from './pages/StudentsPage.vue'
import CurrentScenarioPage from './pages/CurrentScenarioPage.vue'
import ScenariosPage from './pages/ScenariosPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'home', component: HomePage },
        { path: 'settings', name: 'settings', component: SettingsPage },
        { path: 'currentstudent', name: 'currentstudent', component: CurrentStudentPage },
        { path: 'students', name: 'students', component: StudentsPage },
        { path: 'currentscenario', name: 'scenario', component: CurrentScenarioPage },
        { path: 'scenarios', name: 'scenarios', component: ScenariosPage }
      ]
    },
    {
      path: '/camera',
      component: CameraLayout,
      children: [
        { path: '', name: 'camera', component: CameraPage }
      ]
    }
  ]
})
