import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function useClipboard() {
  const isSupported = ref(!!navigator.clipboard)

  async function copy(text) {
    if (!isSupported.value) {
      ElMessage.error('Копирование не поддерживается')
      return false
    }

    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success('Скопировано в буфер обмена')
      return true
    } catch (err) {
      ElMessage.error('Ошибка копирования')
      return false
    }
  }

  return {
    isSupported,
    copy
  }
}