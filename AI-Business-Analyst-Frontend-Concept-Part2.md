# AI-Business Analyst Frontend - Часть 2

## 📦 7. STATE MANAGEMENT СТРАТЕГИЯ <a name="state"></a>

### 7.1 Философия управления состоянием

**Принцип разделения**:
- **Local State** (ref/reactive): Только UI состояние компонента
- **Pinia Stores**: Глобальное состояние, которое нужно в нескольких компонентах
- **Composables**: Переиспользуемая логика без состояния

### 7.2 Chat Store

```javascript
// src/stores/chatStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([])
  const isProcessing = ref(false)
  const currentSessionId = ref(null)
  const error = ref(null)

  // Getters
  const messageCount = computed(() => messages.value.length)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])
  const userMessages = computed(() => 
    messages.value.filter(m => m.role === 'user')
  )
  const assistantMessages = computed(() => 
    messages.value.filter(m => m.role === 'assistant')
  )

  // Actions
  function addMessage(message) {
    const newMessage = {
      id: Date.now() + Math.random(), // Simple ID generation
      role: message.role,
      content: message.content,
      timestamp: new Date().toISOString(),
      layer: message.layer || null,
      document: message.document || null,
      metadata: message.metadata || {}
    }
    
    messages.value.push(newMessage)
    return newMessage
  }

  function updateMessage(messageId, updates) {
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index !== -1) {
      messages.value[index] = {
        ...messages.value[index],
        ...updates
      }
    }
  }

  function deleteMessage(messageId) {
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }
  }

  function clearChat() {
    messages.value = []
    currentSessionId.value = null
    error.value = null
  }

  function setProcessing(value) {
    isProcessing.value = value
  }

  function setError(errorMessage) {
    error.value = errorMessage
  }

  function startNewSession() {
    currentSessionId.value = `session_${Date.now()}`
    clearChat()
  }

  // Persistence
  function saveToLocalStorage() {
    try {
      localStorage.setItem('forte_chat_messages', JSON.stringify(messages.value))
      localStorage.setItem('forte_session_id', currentSessionId.value)
    } catch (error) {
      console.error('Failed to save chat to localStorage:', error)
    }
  }

  function loadFromLocalStorage() {
    try {
      const savedMessages = localStorage.getItem('forte_chat_messages')
      const savedSessionId = localStorage.getItem('forte_session_id')
      
      if (savedMessages) {
        messages.value = JSON.parse(savedMessages)
      }
      if (savedSessionId) {
        currentSessionId.value = savedSessionId
      }
    } catch (error) {
      console.error('Failed to load chat from localStorage:', error)
    }
  }

  return {
    // State
    messages,
    isProcessing,
    currentSessionId,
    error,
    
    // Getters
    messageCount,
    lastMessage,
    userMessages,
    assistantMessages,
    
    // Actions
    addMessage,
    updateMessage,
    deleteMessage,
    clearChat,
    setProcessing,
    setError,
    startNewSession,
    saveToLocalStorage,
    loadFromLocalStorage
  }
})
```

### 7.3 Document Store

```javascript
// src/stores/documentStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDocumentStore = defineStore('document', () => {
  // State
  const documents = ref([])
  const currentDocument = ref(null)
  const isGenerating = ref(false)
  
  // Getters
  const documentCount = computed(() => documents.value.length)
  const documentsByType = computed(() => {
    return documents.value.reduce((acc, doc) => {
      if (!acc[doc.type]) {
        acc[doc.type] = []
      }
      acc[doc.type].push(doc)
      return acc
    }, {})
  })
  const recentDocuments = computed(() => {
    return [...documents.value]
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 5)
  })

  // Actions
  function addDocument(document) {
    const newDoc = {
      id: `doc_${Date.now()}`,
      title: document.title,
      type: document.type, // 'BRD', 'PRD', 'TSD'
      content: document.content,
      mermaidDiagram: document.mermaidDiagram || null,
      quality: document.quality || null,
      metadata: document.metadata || {},
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    documents.value.push(newDoc)
    currentDocument.value = newDoc
    return newDoc
  }

  function updateDocument(documentId, updates) {
    const index = documents.value.findIndex(d => d.id === documentId)
    if (index !== -1) {
      documents.value[index] = {
        ...documents.value[index],
        ...updates,
        updatedAt: new Date().toISOString()
      }
    }
  }

  function deleteDocument(documentId) {
    const index = documents.value.findIndex(d => d.id === documentId)
    if (index !== -1) {
      documents.value.splice(index, 1)
      if (currentDocument.value?.id === documentId) {
        currentDocument.value = null
      }
    }
  }

  function setCurrentDocument(document) {
    currentDocument.value = document
  }

  function clearDocuments() {
    documents.value = []
    currentDocument.value = null
  }

  return {
    documents,
    currentDocument,
    isGenerating,
    documentCount,
    documentsByType,
    recentDocuments,
    addDocument,
    updateDocument,
    deleteDocument,
    setCurrentDocument,
    clearDocuments
  }
})
```

### 7.4 Layer Store

```javascript
// src/stores/layerStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLayerStore = defineStore('layer', () => {
  // State
  const currentLayer = ref(null)
  const layerHistory = ref([])
  const layerData = ref({
    1: { status: 'pending', data: null }, // Intent Understanding
    2: { status: 'pending', data: null }, // Requirement Gathering
    3: { status: 'pending', data: null }, // RAG Search
    4: { status: 'pending', data: null }, // Document Generation
    5: { status: 'pending', data: null }  // Quality Validation
  })

  // Getters
  const currentLayerStatus = computed(() => {
    return currentLayer.value ? layerData.value[currentLayer.value].status : null
  })
  
  const completedLayers = computed(() => {
    return Object.entries(layerData.value)
      .filter(([_, layer]) => layer.status === 'completed')
      .map(([id]) => parseInt(id))
  })

  const progress = computed(() => {
    return (completedLayers.value.length / 5) * 100
  })

  // Actions
  function setCurrentLayer(layer) {
    if (layer >= 1 && layer <= 5) {
      currentLayer.value = layer
      updateLayerStatus(layer, 'active')
      
      layerHistory.value.push({
        layer,
        timestamp: new Date().toISOString()
      })
    }
  }

  function updateLayerStatus(layer, status) {
    if (layerData.value[layer]) {
      layerData.value[layer].status = status
    }
  }

  function updateLayerData(layer, data) {
    if (layerData.value[layer]) {
      layerData.value[layer].data = data
    }
  }

  function completeLayer(layer) {
    updateLayerStatus(layer, 'completed')
    
    // Automatically move to next layer
    if (layer < 5) {
      setCurrentLayer(layer + 1)
    }
  }

  function reset() {
    currentLayer.value = null
    layerHistory.value = []
    Object.keys(layerData.value).forEach(key => {
      layerData.value[key] = { status: 'pending', data: null }
    })
  }

  return {
    currentLayer,
    layerHistory,
    layerData,
    currentLayerStatus,
    completedLayers,
    progress,
    setCurrentLayer,
    updateLayerStatus,
    updateLayerData,
    completeLayer,
    reset
  }
})
```

---

## 🔌 8. API ИНТЕГРАЦИЯ <a name="api"></a>

### 8.1 API Client Setup

```javascript
// src/utils/api/client.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    if (options.body) {
      config.body = JSON.stringify(options.body)
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.message || `HTTP Error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Request Error:', error)
      throw error
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' })
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body })
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', body })
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' })
  }
}

export const apiClient = new APIClient(API_BASE_URL)
```

### 8.2 WebSocket Manager

```javascript
// src/utils/api/websocket.js
export class WebSocketManager {
  constructor(url) {
    this.url = url
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = {}
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
        this.handleReconnect()
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data)
      }
    })
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectDelay * this.reconnectAttempts
      
      console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`)
      
      setTimeout(() => {
        this.connect()
      }, delay)
    }
  }

  send(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback)
    }
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data)
      const { type, ...payload } = message

      if (this.listeners[type]) {
        this.listeners[type].forEach(callback => callback(payload))
      }

      // Emit to 'message' listeners for all messages
      if (this.listeners['message']) {
        this.listeners['message'].forEach(callback => callback(message))
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
```

### 8.3 useChat Composable

```javascript
// src/composables/useChat.js
import { ref } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import { useLayerStore } from '@/stores/layerStore'
import { useDocumentStore } from '@/stores/documentStore'
import { apiClient } from '@/utils/api/client'
import { ElMessage } from 'element-plus'

export function useChat() {
  const chatStore = useChatStore()
  const layerStore = useLayerStore()
  const documentStore = useDocumentStore()

  const isLoading = ref(false)
  const error = ref(null)

  async function sendMessage(content) {
    isLoading.value = true
    error.value = null

    // Add user message to store
    chatStore.addMessage({
      role: 'user',
      content
    })

    try {
      // Call API
      const response = await apiClient.post('/api/chat', {
        message: content,
        session_id: chatStore.currentSessionId,
        history: chatStore.messages.slice(-10) // Last 10 messages for context
      })

      // Update layer
      if (response.current_layer) {
        layerStore.setCurrentLayer(response.current_layer)
      }

      // Add AI response
      const aiMessage = chatStore.addMessage({
        role: 'assistant',
        content: response.response,
        layer: response.current_layer,
        document: response.document || null,
        metadata: response.metadata || {}
      })

      // If document was generated, add to document store
      if (response.document) {
        documentStore.addDocument(response.document)
      }

      // Update layer data
      if (response.layer_data) {
        layerStore.updateLayerData(
          response.current_layer, 
          response.layer_data
        )
      }

      // Complete layer if done
      if (response.layer_complete) {
        layerStore.completeLayer(response.current_layer)
      }

      return aiMessage

    } catch (err) {
      error.value = err.message
      ElMessage.error('Ошибка при отправке сообщения')
      
      chatStore.addMessage({
        role: 'assistant',
        content: 'Извините, произошла ошибка. Попробуйте еще раз.',
        metadata: { error: true }
      })
      
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function regenerateMessage(messageId) {
    // Find the message
    const message = chatStore.messages.find(m => m.id === messageId)
    if (!message || message.role !== 'assistant') return

    // Find previous user message
    const messageIndex = chatStore.messages.findIndex(m => m.id === messageId)
    const previousMessages = chatStore.messages.slice(0, messageIndex)
    const lastUserMessage = previousMessages
      .reverse()
      .find(m => m.role === 'user')

    if (lastUserMessage) {
      // Delete current message
      chatStore.deleteMessage(messageId)
      // Resend user message
      sendMessage(lastUserMessage.content)
    }
  }

  return {
    isLoading,
    error,
    sendMessage,
    regenerateMessage
  }
}
```

### 8.4 useDocument Composable

```javascript
// src/composables/useDocument.js
import { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell } from 'docx'
import { jsPDF } from 'jspdf'
import { saveAs } from 'file-saver'
import { ElMessage } from 'element-plus'

export function useDocument() {
  
  async function generateDOCX(documentData) {
    try {
      const doc = new Document({
        sections: [{
          properties: {
            page: {
              margin: {
                top: 1440,    // 1 inch = 1440 twips
                right: 1440,
                bottom: 1440,
                left: 1440
              }
            }
          },
          children: [
            // Title
            new Paragraph({
              text: documentData.title,
              heading: HeadingLevel.HEADING_1,
              spacing: { after: 400 }
            }),

            // Metadata
            new Paragraph({
              children: [
                new TextRun({
                  text: `Тип: ${documentData.type}`,
                  bold: true
                }),
                new TextRun({
                  text: ` | Дата: ${new Date().toLocaleDateString('ru-RU')}`,
                  break: 1
                })
              ],
              spacing: { after: 400 }
            }),

            // Executive Summary
            new Paragraph({
              text: 'Executive Summary',
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 }
            }),
            new Paragraph({
              text: documentData.executiveSummary || '',
              spacing: { after: 400 }
            }),

            // Requirements
            new Paragraph({
              text: 'Requirements',
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 }
            }),
            ...(documentData.requirements || []).map(req => 
              new Paragraph({
                text: req,
                bullet: { level: 0 },
                spacing: { after: 100 }
              })
            ),

            // Quality Score (if available)
            ...(documentData.quality ? [
              new Paragraph({
                text: 'Quality Assessment',
                heading: HeadingLevel.HEADING_2,
                spacing: { before: 400, after: 200 }
              }),
              new Paragraph({
                children: [
                  new TextRun({
                    text: `Overall Score: ${(documentData.quality.overall * 100).toFixed(0)}%`,
                    bold: true
                  }),
                  new TextRun({
                    text: `\nCompleteness: ${(documentData.quality.completeness * 100).toFixed(0)}%`,
                    break: 1
                  }),
                  new TextRun({
                    text: `\nConsistency: ${(documentData.quality.consistency * 100).toFixed(0)}%`,
                    break: 1
                  })
                ]
              })
            ] : [])
          ]
        }]
      })

      const blob = await Packer.toBlob(doc)
      const filename = `${documentData.type}_${Date.now()}.docx`
      saveAs(blob, filename)
      
      ElMessage.success('Документ DOCX создан успешно')
      return filename

    } catch (error) {
      console.error('Error generating DOCX:', error)
      ElMessage.error('Ошибка создания DOCX документа')
      throw error
    }
  }

  function generatePDF(documentData) {
    try {
      const doc = new jsPDF()
      let yPosition = 20

      // Title
      doc.setFontSize(20)
      doc.setFont(undefined, 'bold')
      doc.text(documentData.title, 20, yPosition)
      yPosition += 15

      // Metadata
      doc.setFontSize(10)
      doc.setFont(undefined, 'normal')
      doc.text(`Тип: ${documentData.type} | Дата: ${new Date().toLocaleDateString('ru-RU')}`, 20, yPosition)
      yPosition += 15

      // Executive Summary
      doc.setFontSize(14)
      doc.setFont(undefined, 'bold')
      doc.text('Executive Summary', 20, yPosition)
      yPosition += 10

      doc.setFontSize(11)
      doc.setFont(undefined, 'normal')
      const summaryLines = doc.splitTextToSize(documentData.executiveSummary || '', 170)
      doc.text(summaryLines, 20, yPosition)
      yPosition += summaryLines.length * 7 + 10

      // Requirements
      if (documentData.requirements && documentData.requirements.length > 0) {
        doc.setFontSize(14)
        doc.setFont(undefined, 'bold')
        doc.text('Requirements', 20, yPosition)
        yPosition += 10

        doc.setFontSize(11)
        doc.setFont(undefined, 'normal')
        documentData.requirements.forEach(req => {
          const lines = doc.splitTextToSize(`• ${req}`, 165)
          doc.text(lines, 25, yPosition)
          yPosition += lines.length * 7
        })
      }

      const filename = `${documentData.type}_${Date.now()}.pdf`
      doc.save(filename)
      
      ElMessage.success('Документ PDF создан успешно')
      return filename

    } catch (error) {
      console.error('Error generating PDF:', error)
      ElMessage.error('Ошибка создания PDF документа')
      throw error
    }
  }

  async function exportDocument(document, format = 'docx') {
    if (format === 'docx') {
      return await generateDOCX(document)
    } else if (format === 'pdf') {
      return generatePDF(document)
    } else {
      throw new Error(`Unsupported format: ${format}`)
    }
  }

  return {
    generateDOCX,
    generatePDF,
    exportDocument
  }
}
```

---

## 🎨 9. UI/UX ПАТТЕРНЫ ДЛЯ БАНКОВСКОГО AI <a name="ux"></a>

### 9.1 Принципы UX для банковского сектора

1. **Доверие и надежность**
   - Консистентный дизайн
   - Профессиональный внешний вид
   - Четкая обратная связь
   - Видимость процессов

2. **Ясность и прозрачность**
   - Понятные инструкции
   - Объяснение каждого шага
   - Визуализация прогресса
   - Нет скрытых действий

3. **Контроль пользователя**
   - Возможность отменить/вернуться
   - Сохранение прогресса
   - Экспорт данных
   - История действий

4. **Производительность**
   - Быстрый отклик
   - Оптимистичные UI обновления
   - Preloading
   - Кэширование

### 9.2 Empty States

```vue
<template>
  <div class="empty-state">
    <div class="empty-state-icon">
      <el-icon :size="80" color="var(--forte-primary)">
        <ChatDotRound />
      </el-icon>
    </div>
    
    <h3 class="empty-state-title">
      Начните новый диалог с AI-аналитиком
    </h3>
    
    <p class="empty-state-description">
      Опишите ваши требования к проекту, и я помогу создать
      профессиональную бизнес-документацию
    </p>
    
    <div class="empty-state-suggestions">
      <el-button
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        @click="$emit('select', suggestion.text)"
        class="suggestion-button"
      >
        {{ suggestion.text }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--forte-space-12);
  max-width: 600px;
  margin: 0 auto;
}

.empty-state-icon {
  margin-bottom: var(--forte-space-6);
  opacity: 0.8;
}

.empty-state-title {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-3);
}

.empty-state-description {
  font-size: var(--forte-text-base);
  color: var(--forte-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--forte-space-8);
}

.empty-state-suggestions {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
  width: 100%;
}

.suggestion-button {
  text-align: left;
  white-space: normal;
  height: auto;
  padding: var(--forte-space-4);
}
</style>
```

### 9.3 Loading States

```vue
<template>
  <div class="loading-state">
    <div class="loading-animation">
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    
    <p class="loading-text">
      {{ loadingText }}
    </p>
    
    <el-progress
      v-if="showProgress"
      :percentage="progress"
      :color="'var(--forte-primary)'"
      :show-text="false"
    />
  </div>
</template>

<style scoped>
.loading-dots {
  display: flex;
  gap: 8px;
}

.loading-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--forte-primary);
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
```

### 9.4 Error States

```vue
<template>
  <div class="error-state">
    <el-result
      icon="error"
      title="Произошла ошибка"
      :sub-title="errorMessage"
    >
      <template #extra>
        <el-button type="primary" @click="$emit('retry')">
          Попробовать снова
        </el-button>
        <el-button @click="$emit('cancel')">
          Отменить
        </el-button>
      </template>
    </el-result>
  </div>
</template>
```

### 9.5 Success Feedback

```javascript
// Используйте Toast notifications для успеха
import { ElMessage } from 'element-plus'

ElMessage({
  message: 'Документ успешно создан!',
  type: 'success',
  duration: 3000,
  showClose: true
})

// Для важных действий используйте модальные окна
ElMessageBox.alert(
  'Ваш BRD документ готов к скачиванию',
  'Генерация завершена',
  {
    confirmButtonText: 'Скачать',
    type: 'success'
  }
)
```

---

## 📅 10. ПЛАН РАЗРАБОТКИ ДЛЯ ХАКАТОНА <a name="план"></a>

### 10.1 Timeline (2-3 дня)

#### День 1: Foundation (8 часов)

**Утро (4 часа)**
- ✅ Инициализация проекта + setup (1h)
  ```bash
  npm create vite@latest
  npm install dependencies
  ```
- ✅ Создание базовой структуры папок (30min)
- ✅ Setup Pinia stores (1h)
- ✅ Создание design system (variables.css) (1h)
- ✅ Настройка Element Plus с кастомной темой (30min)

**Обед** (1 час)

**После обеда (4 часа)**
- ✅ ChatContainer компонент (1.5h)
- ✅ ChatMessage компонент (1h)
- ✅ ChatInput компонент (1h)
- ✅ API client setup (30min)

**Итог Дня 1**: Работающий чат с UI, без бэкенда

---

#### День 2: Core Features (8 часов)

**Утро (4 часа)**
- ✅ Интеграция с бэкендом (useChat composable) (2h)
- ✅ LayerProgress компонент (1h)
- ✅ MermaidChart компонент (1h)

**Обед** (1 час)

**После обеда (4 часа)**
- ✅ Document generation (useDocument composable) (2h)
- ✅ DocumentPreview компонент (1h)
- ✅ Export functionality (1h)

**Итог Дня 2**: Полный функционал генерации

---

#### День 3: Polish & Demo (6 часов)

**Утро (3 часа)**
- ✅ Empty states (30min)
- ✅ Error handling (30min)
- ✅ Loading states (30min)
- ✅ Mobile responsiveness (1h)
- ✅ Тестирование (30min)

**После обеда (3 часа)**
- ✅ UI polish (анимации, переходы) (1h)
- ✅ Подготовка демо данных (30min)
- ✅ Презентация и README (1h)
- ✅ Финальное тестирование (30min)

**Итог Дня 3**: Production-ready демо

---

### 10.2 Prioritization (MoSCoW)

#### Must Have (Критично для MVP)
- ✅ Базовый чат интерфейс
- ✅ Отправка/получение сообщений
- ✅ Визуализация 5 слоев
- ✅ Генерация DOCX/PDF
- ✅ Mermaid диаграммы
- ✅ Базовый Fortebank стиль

#### Should Have (Важно, но не критично)
- ⚠️ История чатов
- ⚠️ Сохранение в localStorage
- ⚠️ Copy/Regenerate функции
- ⚠️ Quality badges
- ⚠️ Responsive design

#### Could Have (Было бы хорошо)
- ⭕ Темная тема
- ⭕ Keyboard shortcuts
- ⭕ Анимации и transitions
- ⭕ Drag & drop для файлов
- ⭕ Rich text editor

#### Won't Have (Не для хакатона)
- ❌ Аутентификация
- ❌ Multi-user support
- ❌ Real-time collaboration
- ❌ Advanced analytics
- ❌ Custom templates

---

### 10.3 Git Workflow (для команды)

```bash
# Branches
main          # Production-ready code
develop       # Integration branch
feature/*     # Feature branches

# Example
git checkout -b feature/chat-input
# ... work ...
git commit -m "feat: add chat input component"
git push origin feature/chat-input
# Create PR to develop
```

**Commit Convention**:
```
feat: new feature
fix: bug fix
style: formatting
refactor: code restructuring
docs: documentation
test: adding tests
```

---

## ⚡ 11. ОПТИМИЗАЦИЯ И ПРОИЗВОДИТЕЛЬНОСТЬ <a name="оптимизация"></a>

### 11.1 Bundle Size Optimization

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'docx': ['docx'],
          'pdf': ['jspdf'],
          'vendor': ['vue', 'pinia']
        }
      }
    }
  }
}
```

### 11.2 Lazy Loading

```javascript
// Lazy load heavy components
const MermaidChart = defineAsyncComponent(() => 
  import('@/components/visualization/MermaidChart.vue')
)

const DocumentPreview = defineAsyncComponent(() =>
  import('@/components/documents/DocumentPreview.vue')
)
```

### 11.3 Debouncing

```javascript
import { useDebounceFn } from '@vueuse/core'

const debouncedSend = useDebounceFn((message) => {
  sendMessage(message)
}, 300)
```

### 11.4 Virtual Scrolling (для больших чатов)

```vue
<el-virtual-scroll :items="messages" :item-height="100">
  <template #default="{ item }">
    <ChatMessage :message="item" />
  </template>
</el-virtual-scroll>
```

---

## 🐛 12. ПОТЕНЦИАЛЬНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ <a name="проблемы"></a>

### Проблема 1: Mermaid не рендерится
**Решение**: Проверьте, что mermaid код валидный и обернут правильно
```javascript
// Bad
const diagram = "graph TD..."

// Good
const diagram = `graph TD
  A --> B`
```

### Проблема 2: DOCX файлы поврежденные
**Решение**: Используйте правильный MIME type
```javascript
const blob = await Packer.toBlob(doc)
// Убедитесь что это Blob, не ArrayBuffer
saveAs(blob, 'document.docx')
```

### Проблема 3: Чат не прокручивается вниз
**Решение**: Используйте nextTick
```javascript
await nextTick()
scrollToBottom()
```

### Проблема 4: Element Plus стили не применяются
**Решение**: Импортируйте CSS в main.js
```javascript
import 'element-plus/dist/index.css'
```

### Проблема 5: Медленная генерация PDF с кириллицей
**Решение**: Используйте правильный шрифт
```javascript
doc.setFont('helvetica') // Supports Cyrillic
```

---

## 🎯 ЗАКЛЮЧЕНИЕ

Эта концепция дает вам:
- ✅ Полную архитектуру фронтенда
- ✅ Готовые компоненты для старта
- ✅ Стратегию разработки
- ✅ Реальные решения проблем

**Следующие шаги**:
1. Клонируйте структуру проекта
2. Начните с Дня 1 плана
3. Итеративно добавляйте функции
4. Тестируйте на каждом этапе

**Удачи на хакатоне! 🚀**