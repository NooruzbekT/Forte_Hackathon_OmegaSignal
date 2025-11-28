import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/utils/api/client'
import { API_ENDPOINTS } from '@/utils/api/endpoints'

export const useChatStore = defineStore('chat', () => {

  // =========================
  // STATE
  // =========================

  const sessions = ref([])                   // список всех чатов
  const currentSessionId = ref(null)         // активная сессия
  const messages = ref([])                   // сообщения текущей сессии
  const isProcessing = ref(false)
  const error = ref(null)


  // =========================
  // GETTERS
  // =========================

  const messageCount = computed(() => messages.value.length)
  const lastMessage = computed(() => messages.value.at(-1))

  const userMessages = computed(() =>
    messages.value.filter(m => m.role === 'user')
  )

  const assistantMessages = computed(() =>
    messages.value.filter(m => m.role === 'assistant')
  )


  // =========================
  // SESSION MANAGEMENT
  // =========================

  async function loadAllSessions() {
    try {
      const resp = await apiClient.get(API_ENDPOINTS.ADMIN_SESSIONS)
      const payload = resp?.data ?? resp

      // предполагаем, что backend вернёт { sessions: [...] }
      sessions.value = payload.sessions || []
    } catch (err) {
      console.error('Failed to load sessions:', err)
    }
  }


  function setActiveSession(sessionId) {
    currentSessionId.value = sessionId

    // если такой сессии ещё нет в списке — добавим
    const exists = sessions.value.some(s => s.session_id === sessionId)
    if (!exists) {
      sessions.value.push({
        session_id: sessionId,
        created_at: new Date().toISOString(),
        last_message: null
      })
    }
  }


  function startNewSession() {
    const id = `session_${Date.now()}`
    currentSessionId.value = id

    // Добавляем в историю чатов
    sessions.value.push({
      session_id: id,
      created_at: new Date().toISOString(),
      last_message: null
    })

    clearMessages()
    return id
  }

  // =========================
  // MESSAGE MANAGEMENT
  // =========================

  function addMessage(message) {
    const newMessage = {
      id: Date.now() + Math.random(),
      role: message.role,
      content: message.content,
      timestamp: new Date().toISOString(),
      layer: message.layer || null,
      document: message.document || null,
      metadata: message.metadata || {}
    }

    messages.value.push(newMessage)

    // обновляем last_message у текущей сессии
    const session = sessions.value.find(s => s.session_id === currentSessionId.value)
    if (session) session.last_message = newMessage.content.slice(0, 100)

    // сохраняем локально
    saveSessionToLocal(currentSessionId.value)

    return newMessage
  }

  function updateMessage(id, updates) {
    const idx = messages.value.findIndex(m => m.id === id)
    if (idx !== -1) {
      messages.value[idx] = { ...messages.value[idx], ...updates }
      saveSessionToLocal(currentSessionId.value)
    }
  }

  function deleteMessage(id) {
    messages.value = messages.value.filter(m => m.id !== id)
    saveSessionToLocal(currentSessionId.value)
  }

  function clearMessages() {
    messages.value = []
  }

  // =========================
  // HISTORY LOADING
  // =========================

  async function loadSessionHistory(sessionId) {
    try {
      // пробуем взять из localStorage сначала
      if (loadSessionFromLocal(sessionId)) {
        currentSessionId.value = sessionId
        return
      }

      const resp = await apiClient.get(API_ENDPOINTS.HISTORY_GET(sessionId))
      const payload = resp?.data ?? resp

      messages.value = payload.messages || []
      currentSessionId.value = sessionId

      saveSessionToLocal(sessionId)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  // =========================
  // LOCAL STORAGE
  // =========================

  function saveSessionToLocal(sessionId) {
    try {
      localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages.value))
    } catch {}
  }

  function loadSessionFromLocal(sessionId) {
    try {
      const data = localStorage.getItem(`chat_${sessionId}`)
      if (!data) return false

      messages.value = JSON.parse(data)
      return true
    } catch {
      return false
    }
  }

  function loadAllLocalSessions() {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('chat_'))
    keys.forEach(k => {
      sessions.value.push({
        session_id: k.replace('chat_', ''),
        created_at: null,
        last_message: '(offline)'
      })
    })
  }


  // =========================
  // PROCESSING / ERROR
  // =========================

  function setProcessing(val) {
    isProcessing.value = val
  }

  function setError(val) {
    error.value = val
  }


  return {
    // state
    messages,
    sessions,
    currentSessionId,
    isProcessing,
    error,

    // getters
    messageCount,
    lastMessage,
    userMessages,
    assistantMessages,

    // session
    loadAllSessions,
    loadAllLocalSessions,
    startNewSession,
    setActiveSession,
    loadSessionHistory,

    // messages
    addMessage,
    updateMessage,
    deleteMessage,
    clearMessages,

    // flags
    setProcessing,
    setError
  }
})
