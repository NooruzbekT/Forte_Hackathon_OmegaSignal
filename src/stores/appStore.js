import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const theme = ref('light')
  const isLoading = ref(false)
  const notification = ref(null)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setTheme(newTheme) {
    theme.value = newTheme
  }

  function setLoading(value) {
    isLoading.value = value
  }

  function showNotification(message, type = 'info') {
    notification.value = { message, type, timestamp: Date.now() }
  }

  return {
    sidebarCollapsed,
    theme,
    isLoading,
    notification,
    toggleSidebar,
    setTheme,
    setLoading,
    showNotification
  }
})