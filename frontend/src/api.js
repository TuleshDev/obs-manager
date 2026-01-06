import axios from 'axios'

function handleResponse(promise) {
  return promise
    .then((response) => {
      const data = response.data
      if (data.status && data.status === 'error') {
        throw new Error(data.message || 'Неизвестная ошибка')
      }
      return data
    })
    .catch((error) => {
      if (error.response && error.response.data) {
        throw new Error(error.response.data.message || 'Ошибка сервера')
      } else {
        throw new Error(error.message || 'Ошибка соединения')
      }
    })
}

export const api = {
  getConfig: (scenarioName = null) => {
    const url = scenarioName
      ? `/api/config?scenario=${encodeURIComponent(scenarioName)}`
      : '/api/config'
    return handleResponse(axios.get(url))
  },
  updateConfig: (cfg) => {
    return handleResponse(axios.put('/api/config', cfg))
  },
  restoreBackup: (scenarioName) => {
    return handleResponse(axios.post(`/api/backup/restore/${scenarioName}`))
  },
  listDevices: () => handleResponse(axios.get('/api/devices')),
  apply: (cfg) => {
    return handleResponse(axios.post('/api/apply', cfg))
  },

  listStudents: () => handleResponse(axios.get('/api/students')),
  getStudent: (id) => handleResponse(axios.get(`/api/students/${id}`)),
  createStudent: (student) => handleResponse(axios.post('/api/students', student)),
  updateStudent: (id, student) => handleResponse(axios.put(`/api/students/${id}`, student)),
  deleteStudent: (id) => handleResponse(axios.delete(`/api/students/${id}`)),

  listScenarios: () => handleResponse(axios.get('/api/scenarios')),
  getScenario: (id) => handleResponse(axios.get(`/api/scenarios/${id}`)),
  createScenario: (scenario) => handleResponse(axios.post('/api/scenarios', scenario)),
  updateScenario: (id, scenario) => handleResponse(axios.put(`/api/scenarios/${id}`, scenario)),
  deleteScenario: (id) => handleResponse(axios.delete(`/api/scenarios/${id}`)),
  assignScenario: (studentId, scenarioId) =>
    handleResponse(axios.post(`/api/students/${studentId}/scenarios/${scenarioId}`))
}
