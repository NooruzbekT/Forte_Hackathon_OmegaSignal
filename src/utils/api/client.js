class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  }

  async request(url, options = {}) {
    const config = {
      headers: {
        ...options.headers
      },
      ...options
    }

    // Добавляем Content-Type только если нет FormData
    if (!(options.body instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
    }

    try {
      const response = await fetch(`${this.baseURL}${url}`, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`)
      }

      // Проверяем тип контента
      const contentType = response.headers.get('content-type')
      
      if (contentType && contentType.includes('application/json')) {
        return await response.json()
      }
      
      // Для файлов возвращаем blob
      if (contentType && (contentType.includes('application/') || contentType.includes('image/'))) {
        return await response.blob()
      }
      
      return await response.text()
    } catch (error) {
      console.error('API Request Error:', error)
      throw error
    }
  }

  async get(url, options = {}) {
    return this.request(url, {
      method: 'GET',
      ...options
    })
  }

  async post(url, body, options = {}) {
    const config = { method: 'POST', ...options }
    
    // Если body это FormData, передаём как есть
    if (body instanceof FormData) {
      config.body = body
    } else {
      config.body = JSON.stringify(body)
    }
    
    return this.request(url, config)
  }

  async put(url, body, options = {}) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(body),
      ...options
    })
  }

  async delete(url, options = {}) {
    return this.request(url, {
      method: 'DELETE',
      ...options
    })
  }

  // Скачивание файла
  async downloadFile(url, filename) {
    try {
      const blob = await this.get(url)
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('Download error:', error)
      throw error
    }
  }
}

export const apiClient = new APIClient()