import { ref } from 'vue'

const message = ref('')
const type = ref('success')
const show = ref(false)

export function useSnackbar() {
  const showMessage = (msg, msgType = 'success') => {
    message.value = msg
    type.value = msgType
    show.value = true

    if (type.value !== 'error') {
      setTimeout(() => {
        show.value = false
      }, 3000)
    }
  }

  return {
    message,
    type,
    show,
    showMessage
  }
}
