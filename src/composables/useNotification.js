import { ElMessage, ElNotification } from 'element-plus'

export function useNotification() {
  function success(message) {
    ElMessage.success(message)
  }

  function error(message) {
    ElMessage.error(message)
  }

  function warning(message) {
    ElMessage.warning(message)
  }

  function info(message) {
    ElMessage.info(message)
  }

  function notify(title, message, type = 'info') {
    ElNotification({
      title,
      message,
      type,
      duration: 3000
    })
  }

  return {
    success,
    error,
    warning,
    info,
    notify
  }
}