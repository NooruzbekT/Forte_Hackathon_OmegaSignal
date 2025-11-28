export function setupInterceptors(apiClient) {
  apiClient.interceptRequest((config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    config.headers['X-Request-Time'] = new Date().toISOString()
    
    return config
  })

  apiClient.interceptResponse(
    (response) => {
      return response
    },
    (error) => {
      if (error.response) {
        switch (error.response.status) {
          case 401:
            console.error('Unauthorized access')
            break
          case 403:
            console.error('Forbidden')
            break
          case 404:
            console.error('Resource not found')
            break
          case 500:
            console.error('Server error')
            break
        }
      }
      return Promise.reject(error)
    }
  )
}