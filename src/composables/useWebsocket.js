import { ref, onUnmounted } from 'vue'

export function useWebSocket(url) {
  const ws = ref(null)
  const isConnected = ref(false)
  const error = ref(null)
  const messageHandlers = new Map()

  function connect() {
    try {
      ws.value = new WebSocket(url)

      ws.value.onopen = () => {
        isConnected.value = true
        error.value = null
      }

      ws.value.onclose = () => {
        isConnected.value = false
      }

      ws.value.onerror = (err) => {
        error.value = err
        isConnected.value = false
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const handler = messageHandlers.get(data.type)
          if (handler) {
            handler(data)
          }
        } catch (err) {
          console.error('WebSocket message error:', err)
        }
      }
    } catch (err) {
      error.value = err
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
  }

  function send(data) {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(data))
    }
  }

  function on(type, handler) {
    messageHandlers.set(type, handler)
  }

  function off(type) {
    messageHandlers.delete(type)
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    error,
    connect,
    disconnect,
    send,
    on,
    off
  }
}