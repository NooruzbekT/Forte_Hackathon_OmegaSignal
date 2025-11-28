import { ref } from 'vue'
import { useChatStore } from '../stores/chatStore'
import { useLayerStore } from '../stores/layerStore'
import { useDocumentStore } from '../stores/documentStore'
import { apiClient } from '../utils/api/client'
import { API_ENDPOINTS } from '../utils/api/endpoints'
import { wsManager } from '../utils/api/websocket'
import { ElMessage } from 'element-plus'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// --------------------------
// MOCK API
// --------------------------
const mockAPI = {
  async sendMessage(message) {
    await new Promise(resolve => setTimeout(resolve, 1500))

    const responses = [
      {
        message: `Понял ваш запрос: "${message}". Начинаю анализ требований...`,
        layer: 1,
        progress: 0.25,
        session_id: 'mock_session'
      },
      {
        message: 'Ищу похожие проекты в базе знаний...',
        layer: 2,
        progress: 0.5,
        session_id: 'mock_session'
      },
      {
        message: 'Создаю BRD документ...',
        layer: 3,
        progress: 0.75,
        session_id: 'mock_session',
        document: {
          filename: 'BRD_document.docx',
          type: 'BRD',
          title: 'Business Requirements Document'
        }
      }
    ]

    return responses[Math.floor(Math.random() * responses.length)]
  }
}

export function useChat() {

  const chatStore = useChatStore()
  const layerStore = useLayerStore()
  const documentStore = useDocumentStore()

  const isLoading = ref(false)
  const error = ref(null)
  const wsConnected = ref(false)

  async function connectWebSocket() {
    const WS_ENABLED = import.meta.env.VITE_WS_ENABLED !== 'false'
    if (!WS_ENABLED || USE_MOCK) return

    if (!chatStore.currentSessionId || chatStore.currentSessionId === 'null') {
      console.warn('Нет sessionId для WebSocket, подключение пропущено')
      return
    }


    try {
      await wsManager.connect(chatStore.currentSessionId)
      wsConnected.value = true

      wsManager.on('layer_update', (data) => {
        console.log('Layer update (WS):', data)

        const totalLayers = layerStore.totalLayers || 5
        let newLayer = data.layer

        // если бек скажет, что документ готов – сразу на последний шаг
        if (data.document_ready) {
          newLayer = totalLayers
        } else if (newLayer === undefined && typeof data.progress === 'number') {
          const p = Math.max(0, Math.min(1, data.progress))
          newLayer = Math.max(1, Math.ceil(p * totalLayers))
        }

        if (newLayer !== undefined) {
          layerStore.setCurrentLayer(newLayer)
        }
      })



      // WebSocket: текстовые сообщения
      wsManager.on('message', (data) => {
        console.log('WS message:', data)

        const content = data.message || data.response || data.content
        if (content) {
          chatStore.addMessage({
            role: 'assistant',
            content,
            layer: data.layer,
            metadata: data.metadata || {}
          })
        }

        if (data.document) {
          documentStore.addDocument({
            ...data.document,
            sessionId: chatStore.currentSessionId
          })
        }
      })

      // WebSocket: документ готов
      wsManager.on('document_generated', (data) => {
        if (data.document) {
          documentStore.addDocument({
            ...data.document,
            sessionId: chatStore.currentSessionId
          })
          ElMessage.success('Документ сгенерирован')
        }
      })

    } catch (err) {
      console.warn('WebSocket error:', err)
      wsConnected.value = false
    }
  }

// --------------------------
// SEND MESSAGE
// --------------------------
async function sendMessage(content) {
  isLoading.value = true
  error.value = null
  chatStore.setProcessing(true)

  // Добавляем сообщение пользователя в чат
  chatStore.addMessage({ role: 'user', content })

  try {
    let rawResponse

    if (USE_MOCK) {
      rawResponse = await mockAPI.sendMessage(content)
    } else {
      const httpResponse = await apiClient.post(API_ENDPOINTS.CHAT, {
        message: content,
        session_id: chatStore.currentSessionId
      })

      rawResponse = httpResponse?.data ?? httpResponse
    }

    console.log('Ответ от бэкенда:', rawResponse)

    // Синхронизируем sessionId с бэкендом
    if (rawResponse.session_id) {
      chatStore.setActiveSession(rawResponse.session_id)
    }

    const totalLayers = layerStore.totalLayers || 5

    // обновление "слоя" воронки
    if (
      rawResponse.layer !== undefined ||
      typeof rawResponse.progress === 'number' ||
      rawResponse.document_ready
    ) {
      let newLayer = rawResponse.layer

      if (rawResponse.document_ready) {
        newLayer = totalLayers
      } else if (newLayer === undefined && typeof rawResponse.progress === 'number') {
        const p = Math.max(0, Math.min(1, rawResponse.progress))
        newLayer = Math.max(1, Math.ceil(p * totalLayers))
      }

      console.log('Обновление слоя (HTTP):', newLayer)
      layerStore.setCurrentLayer(newLayer)
    }

    // текст ассистента
    let assistantText = rawResponse.message

    if (!assistantText) {
      if (!rawResponse.document_ready) {
        assistantText =
          rawResponse.response ||
          rawResponse.data?.message ||
          rawResponse.data?.response
      } else {
        assistantText = 'Документ создан и доступен во вкладке «Документы».'
      }
    }

    let aiMsg = null

    // Сообщение ассистента через HTTP показываем только если WS не подключён
    if (assistantText && !wsConnected.value) {
      aiMsg = chatStore.addMessage({
        role: 'assistant',
        content: assistantText,
        layer: rawResponse.layer,
        metadata: {
          sessionId: rawResponse.session_id,
          docType: rawResponse.doc_type,
          progress: rawResponse.progress,
          documentReady: rawResponse.document_ready
        }
      })
    }

    // 🔥 ДОКУМЕНТ: добавляем в documentStore ВСЕГДА, если он есть в ответе

    // 🔥 ДОКУМЕНТ: добавляем в documentStore ВСЕГДА, если backend сказал document_ready

  if (rawResponse.document) {
    // вариант, когда backend сразу возвращает объект документа
    documentStore.addDocument({
      ...rawResponse.document,
      sessionId: chatStore.currentSessionId
    })
    console.log('Документ добавлен (document):', rawResponse.document)

  } else if (rawResponse.document_ready && rawResponse.doc_type) {
    // backend сказал, что документ готов, но объект/путь не прислал

    const fullPath =
      rawResponse.document_path ||
      rawResponse.doc_path ||
      rawResponse.file_path ||
      rawResponse.doc_file_path ||
      rawResponse.url ||
      null

    const fallbackId = `doc_${Date.now()}`
    const titleFromType = {
      integration: 'Integration Requirements Document',
      brd: 'Business Requirements Document',
      'ai-baproto': 'AI BA Prototype Document'
      // добавишь свои типы по мере надобности
    }

    const filename =
      rawResponse.file_name ||
      (fullPath ? fullPath.split('\\').pop().split('/').pop() : `${rawResponse.doc_type}.docx`)

    documentStore.addDocument({
      id: rawResponse.document_id || fallbackId,
      sessionId: chatStore.currentSessionId,
      type: rawResponse.doc_type,
      title: rawResponse.title || titleFromType[rawResponse.doc_type] || `Document: ${rawResponse.doc_type}`,
      filename,
      document_path: fullPath,     // может быть null
      status: 'ready',
      createdAt: new Date().toISOString()
    })

    console.log('Документ добавлен (ready, без объекта):', {
      id: rawResponse.document_id || fallbackId,
      type: rawResponse.doc_type,
      path: fullPath
    })
  }


    return aiMsg
  } catch (err) {
    console.error('Ошибка отправки:', err)

    const msg = String(err.message || '')


    if (msg.includes('429')) {
      ElMessage.error('Лимит запросов к AI временно превышен. Подождите немного и попробуйте ещё раз.')
    } else {
      ElMessage.error(`Ошибка: ${err.message}`)
    }

    chatStore.addMessage({
      role: 'assistant',
      content: 'Извините, сервис временно перегружен. Попробуйте отправить запрос чуть позже.',
      metadata: { error: true }
    })

    throw err
  } finally {
    isLoading.value = false
    chatStore.setProcessing(false)
  }
}


  async function loadSessionHistory() {
    if (USE_MOCK) return

    try {
      const response = await apiClient.get(
        API_ENDPOINTS.HISTORY_GET(chatStore.currentSessionId)
      )

      const payload = response?.data ?? response

      if (payload.messages) {
        payload.messages.forEach(msg => chatStore.addMessage(msg))
      }

    } catch (err) {
      console.error('History load error:', err)
    }
  }

  // --------------------------
  // GET SESSION INFO
  // --------------------------
  async function getSessionInfo() {
    if (USE_MOCK) return null

    try {
      const response = await apiClient.get(
        API_ENDPOINTS.SESSION_INFO(chatStore.currentSessionId)
      )
      return response?.data ?? response

    } catch {
      return null
    }
  }

  // --------------------------
  // RESET SESSION
  // --------------------------
  async function resetSession() {
    if (USE_MOCK) {
      chatStore.startNewSession()
      layerStore.reset()
      return
    }

    try {
      await apiClient.post(
        API_ENDPOINTS.SESSION_RESET(chatStore.currentSessionId),
        {}
      )
      chatStore.startNewSession()
      layerStore.reset()
      ElMessage.success('Сессия сброшена')

    } catch (err) {
      ElMessage.error('Ошибка сброса сессии')
    }
  }

  // --------------------------
  // SUMMARY
  // --------------------------
  async function generateSummary() {
    if (USE_MOCK) return null

    try {
      const resp = await apiClient.post(
        API_ENDPOINTS.SESSION_SUMMARY(chatStore.currentSessionId),
        {}
      )
      ElMessage.success('Саммари сгенерировано')
      return resp?.data ?? resp

    } catch (err) {
      ElMessage.error('Ошибка генерации саммари')
    }
  }

  return {
    isLoading,
    error,
    wsConnected,
    sendMessage,
    connectWebSocket,
    loadSessionHistory,
    getSessionInfo,
    resetSession,
    generateSummary
  }
}
