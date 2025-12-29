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
  getConfig: () => handleResponse(axios.get('/api/config')),
  updateConfig: (cfg) => handleResponse(axios.put('/api/config', cfg)),
  listDevices: () => handleResponse(axios.get('/api/devices')),
  apply: () => handleResponse(axios.post('/api/apply')),

  listStudents: () => handleResponse(axios.get('/api/students')),
  getStudent: (id) => handleResponse(axios.get(`/api/students/${id}`)),
  createStudent: (student) => handleResponse(axios.post('/api/students', student)),
  updateStudent: (id, student) => handleResponse(axios.put(`/api/students/${id}`, student)),
  deleteStudent: (id) => handleResponse(axios.delete(`/api/students/${id}`))
}
