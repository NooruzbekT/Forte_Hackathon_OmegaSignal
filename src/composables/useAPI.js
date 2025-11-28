import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function useAPI() {
  const isLoading = ref(false)
  const error = ref(null)

  async function request(url, options = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function get(url, options = {}) {
    return request(url, { method: 'GET', ...options })
  }

  async function post(url, body, options = {}) {
    return request(url, {
      method: 'POST',
      body: JSON.stringify(body),
      ...options
    })
  }

  return {
    isLoading,
    error,
    get,
    post,
    request
  }
}