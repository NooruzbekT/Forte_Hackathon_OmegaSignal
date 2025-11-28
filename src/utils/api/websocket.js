class WebSocketManager {
  constructor() {
    this.baseURL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.handlers = new Map()
    this.isConnecting = false
  }

  connect(sessionId) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve()
    }

    this.isConnecting = true

    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.baseURL}/ws/${sessionId}`
        console.log('Connecting to WebSocket:', wsUrl)
        
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected')
          this.reconnectAttempts = 0
          this.isConnecting = false
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('WebSocket message:', data)
            this.handleMessage(data)
          } catch (error) {
            console.error('WebSocket message parse error:', error)
          }
        }

        this.ws.onerror = (error) => {
          // Тихо логируем ошибку без reject
          console.warn('WebSocket connection error (will retry if configured)')
          this.isConnecting = false
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          
          // Пытаемся переподключиться
          if (event.code !== 1000) {
            this.attemptReconnect(sessionId)
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  attemptReconnect(sessionId) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
      
      console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(sessionId).catch(err => {
          console.error('Reconnection failed:', err)
        })
      }, delay)
    } else {
      console.error('❌ Max reconnection attempts reached')
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  on(event, handler) {
    this.handlers.set(event, handler)
  }

  off(event) {
    this.handlers.delete(event)
  }

  handleMessage(data) {
    // Обработка разных типов сообщений
    if (data.type) {
      const handler = this.handlers.get(data.type)
      if (handler) {
        handler(data)
      }
    }
    
    // Обработка сообщений по полям
    if (data.layer !== undefined) {
      const layerHandler = this.handlers.get('layer_update')
      if (layerHandler) layerHandler(data)
    }
    
    if (data.message || data.content) {
      const messageHandler = this.handlers.get('message')
      if (messageHandler) messageHandler(data)
    }
    
    if (data.document) {
      const docHandler = this.handlers.get('document_generated')
      if (docHandler) docHandler(data)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
    this.handlers.clear()
    this.reconnectAttempts = 0
  }

  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

export const wsManager = new WebSocketManager()