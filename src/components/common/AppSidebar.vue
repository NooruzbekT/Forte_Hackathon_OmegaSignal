<script setup>
import { ref, computed, onMounted } from 'vue'
import { ChatDotRound, Document, List, Delete, Download, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useChatStore } from '@/stores/chatStore'
import { useDocumentStore } from '@/stores/documentStore'
import { formatDate } from '@/utils/formatters/dateFormatter'

// STORES
const chatStore = useChatStore()
const documentStore = useDocumentStore()

// UI STATE
const activeTab = ref('chat')

// COMPUTED
const messageCount = computed(() => chatStore.messageCount)
const documentCount = computed(() => documentStore.documentCount)
const sessions = computed(() => chatStore.sessions)
const currentSessionId = computed(() => chatStore.currentSessionId)
const allDocuments = computed(() => documentStore.documents)
const isLoadingDocuments = computed(() => documentStore.isLoading)

function setActiveTab(tab) {
  activeTab.value = tab
  
  // При переключении на вкладку документов - перезагружаем список
  if (tab === 'documents') {
    refreshDocuments()
  }
}

// ----------------------------
// ОТКРЫТЬ ЧАТ ИЗ САЙДБАРА
// ----------------------------
async function openChat(sessionId) {
  try {
    await chatStore.loadSessionHistory(sessionId)
    // Если есть функция подключения WebSocket - вызываем её
    if (chatStore.connectWebSocket) {
      await chatStore.connectWebSocket(sessionId)
    }
    activeTab.value = 'chat'
  } catch (err) {
    console.error('Ошибка загрузки сессии:', err)
    ElMessage.error('Не удалось загрузить сессию')
  }
}

// ----------------------------
// ДОКУМЕНТЫ
// ----------------------------
async function refreshDocuments() {
  try {
    await documentStore.fetchAllDocuments()
  } catch (err) {
    console.error('Ошибка обновления документов:', err)
    ElMessage.error('Не удалось загрузить документы')
  }
}

async function handleDeleteDocument(doc) {
  try {
    await ElMessageBox.confirm(
      `Вы уверены, что хотите удалить документ "${doc.filename}"?`,
      'Подтверждение удаления',
      {
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена',
        type: 'warning',
      }
    )

    await documentStore.deleteDocument(doc.filename)
    ElMessage.success('Документ успешно удалён')
  } catch (err) {
    if (err !== 'cancel') {
      console.error('Ошибка удаления:', err)
      ElMessage.error('Не удалось удалить документ')
    }
  }
}

async function handleDownloadDocument(doc) {
  try {
    await documentStore.downloadDocument(doc.filename)
    ElMessage.success('Документ успешно скачан')
  } catch (err) {
    console.error('Ошибка скачивания:', err)
    ElMessage.error('Не удалось скачать документ')
  }
}

// ----------------------------
// СЕССИИ (ЧАТЫ)
// ----------------------------
async function handleDeleteSession(sessionId) {
  try {
    await ElMessageBox.confirm(
      `Вы уверены, что хотите удалить сессию "${sessionId}"?`,
      'Подтверждение удаления',
      {
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена',
        type: 'warning',
      }
    )

    // Отправляем запрос на бэкенд для удаления истории сессии
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // Удаляем сессию из стора
    if (chatStore.deleteSession) {
      await chatStore.deleteSession(sessionId)
    }

    // Если удалили текущую сессию - сбрасываем её
    if (sessionId === currentSessionId.value) {
      if (chatStore.resetCurrentSession) {
        chatStore.resetCurrentSession()
      }
    }

    // Перезагружаем список сессий
    await chatStore.loadAllSessions()
    
    ElMessage.success('Сессия успешно удалена')
  } catch (err) {
    if (err !== 'cancel') {
      console.error('Ошибка удаления сессии:', err)
      ElMessage.error('Не удалось удалить сессию')
    }
  }
}

async function handleGenerateSummary(sessionId) {
  try {
    const loadingMessage = ElMessage({
      message: 'Генерация сводки...',
      type: 'info',
      duration: 0,
      icon: DocumentCopy
    })

    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${API_BASE_URL}/api/session/${sessionId}/summary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    loadingMessage.close()

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // Форматируем key points в список
    const keyPointsHtml = data.key_points
      .map(point => `• ${point}`)
      .join('<br/>')

    // Показываем сводку в красивом диалоге
    await ElMessageBox.alert(
      `
        <div style="text-align: left;">
          <h3 style="margin-top: 0; color: var(--el-color-primary);">Сводка по сессии</h3>
          <p><strong>Сессия ID:</strong> ${data.session_id}</p>
          <p><strong>Тип документа:</strong> ${data.doc_type || 'Не указан'}</p>
          <p><strong>Всего сообщений:</strong> ${data.total_messages}</p>
          <hr style="margin: 16px 0; border: none; border-top: 1px solid #eee;"/>
          <h4 style="margin-bottom: 8px;">Краткое описание:</h4>
          <p style="line-height: 1.6;">${data.summary}</p>
          <h4 style="margin-bottom: 8px; margin-top: 16px;">Ключевые моменты:</h4>
          <p style="line-height: 1.8;">${keyPointsHtml}</p>
        </div>
      `,
      'AI Сводка',
      {
        confirmButtonText: 'Закрыть',
        dangerouslyUseHTMLString: true,
        customClass: 'summary-dialog'
      }
    )

    ElMessage.success('Сводка успешно создана')
  } catch (err) {
    console.error('Ошибка генерации сводки:', err)
    ElMessage.error('Не удалось создать сводку')
  }
}

// ----------------------------
// LIFECYCLE
// ----------------------------
onMounted(async () => {
  console.log('AppSidebar mounted')
  
  try {
    // 1. Загружаем все документы с бэка
    await documentStore.fetchAllDocuments()
    
    // 2. Загружаем список сессий
    await chatStore.loadAllSessions()
    chatStore.loadAllLocalSessions()
  } catch (err) {
    console.error('Ошибка инициализации сайдбара:', err)
  }
})
</script>

<template>
  <aside class="app-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Workspace</span>
    </div>

    <nav class="sidebar-tabs">
      <div
        :class="['tab-item', { active: activeTab === 'chat' }]"
        @click="setActiveTab('chat')"
      >
        <el-icon :size="20"><ChatDotRound /></el-icon>
        <span>Чат</span>
      </div>

      <div
        :class="['tab-item', { active: activeTab === 'documents' }]"
        @click="setActiveTab('documents')"
      >
        <el-icon :size="20"><Document /></el-icon>
        <span>Документы</span>
        <el-badge v-if="documentCount > 0" :value="documentCount" />
      </div>

      <div
        :class="['tab-item', { active: activeTab === 'history' }]"
        @click="setActiveTab('history')"
      >
        <el-icon :size="20"><List /></el-icon>
        <span>История чатов</span>
      </div>
    </nav>

    <!-- TAB CONTENT -->
    <div class="sidebar-content">
      <!-- ЧАТ -->
      <div v-if="activeTab === 'chat'" class="content-section">
        <h3 class="section-title">Текущая сессия</h3>

        <el-empty
          v-if="!currentSessionId"
          description="Сессия ещё не создана"
          :image-size="60"
        />

        <div v-else class="chat-info">
          <div class="info-item">
            <span class="info-label">ID:</span>
            <el-tag 
              type="primary"
              color="var(--forte-bg-primary)"
            >
              {{ currentSessionId }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">Сообщений:</span>
            <el-tag 
              type="primary"
              color="var(--forte-bg-primary)"
            >
              {{ messageCount }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- ДОКУМЕНТЫ -->
      <div v-if="activeTab === 'documents'" class="content-section">
        <div class="section-header">
          <h3 class="section-title">Документы</h3>
          <el-button 
            size="small" 
            @click="refreshDocuments"
            :loading="isLoadingDocuments"
          >
            Обновить
          </el-button>
        </div>

        <el-empty
          v-if="!isLoadingDocuments && allDocuments.length === 0"
          description="Документы ещё не созданы"
          :image-size="60"
        />

        <div v-else-if="isLoadingDocuments" class="loading-container">
          <el-icon class="is-loading" :size="40">
            <Loading />
          </el-icon>
          <p>Загрузка документов...</p>
        </div>

        <div v-else class="documents-list">
          <div
            v-for="doc in allDocuments"
            :key="doc.id || doc.filename"
            class="document-item"
          >
            <div class="doc-header">
              <el-tag 
                :type="doc.type === 'BRD' ? 'success' : 
                       doc.type === 'INTEGRATION' ? 'primary' : 
                       doc.type === 'BUG_FIX' ? 'danger' : 
                       'warning'" 
                size="small"
              >
                {{ doc.type || 'DOC' }}
              </el-tag>
            </div>
            
            <p class="doc-title" :title="doc.title || doc.filename">
              {{ doc.title || doc.filename || 'Документ' }}
            </p>

            <p class="doc-date">
              {{ formatDate(doc.createdAt || doc.created, 'short') }}
            </p>
            
            <div class="doc-actions">
              <el-button
                size="small"
                :icon="Download"
                @click="handleDownloadDocument(doc)"
                circle
              />
              <el-button
                size="small"
                :icon="Delete"
                type="danger"
                @click="handleDeleteDocument(doc)"
                circle
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ИСТОРИЯ ЧАТОВ -->
      <div v-if="activeTab === 'history'" class="content-section">
        <h3 class="section-title">История чатов</h3>
        
        <el-empty
          v-if="sessions.length === 0"
          description="Нет сохранённых сессий"
          :image-size="60"
        />

        <div v-else class="session-list">
          <div
            class="session-item"
            v-for="s in sessions"
            :key="s.session_id"
            :class="{ active: s.session_id === currentSessionId }"
          >
            <div class="session-content" @click="openChat(s.session_id)">
              <div class="session-id">{{ s.session_id }}</div>
              <div class="session-meta">
                {{ s.last_message ?? '...' }}
              </div>
            </div>
            <div class="session-actions">
              <el-button
                size="small"
                :icon="DocumentCopy"
                type="primary"
                @click.stop="handleGenerateSummary(s.session_id)"
                circle
                title="Создать сводку"
              />
              <el-button
                size="small"
                :icon="Delete"
                type="danger"
                @click.stop="handleDeleteSession(s.session_id)"
                circle
                title="Удалить сессию"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 320px;
  background: white;
  border-right: 1px solid var(--forte-border-light);
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-header {
  padding: var(--forte-space-6);
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  border-bottom: 1px solid var(--forte-border-light);
  background: var(--forte-bg-primary);
}

.sidebar-title {
  font-size: var(--forte-text-lg);
  font-weight: var(--forte-font-bold);
  color: white;
}

.sidebar-tabs {
  padding: var(--forte-space-4);
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
  border-bottom: 1px solid var(--forte-border-light);
  background: var(--forte-bg-primary);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  padding: var(--forte-space-3);
  border-radius: var(--forte-radius-md);
  cursor: pointer;
  transition: all var(--forte-transition-fast);
  color: white;
}

.tab-item:hover {
  background: var(--forte-bg-secondary);
}

.tab-item.active {
  background: var(--forte-primary-lighter);
  color: var(--forte-primary);
  font-weight: var(--forte-font-semibold);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--forte-space-4);
  background: var(--forte-bg-primary);
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-4);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: var(--forte-text-base);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-secondary);
  margin: 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--forte-space-6);
  gap: var(--forte-space-3);
  color: var(--forte-text-secondary);
}

.chat-info {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--forte-space-3);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
}

.info-label {
  font-size: var(--forte-text-xl);
  color: white;
  font-weight: var(--forte-font-medium);
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
}

.document-item {
  padding: var(--forte-space-3);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
  transition: all var(--forte-transition-fast);
  cursor: default;
}

.document-item:hover {
  background: var(--forte-primary-lighter);
  transform: translateX(4px);
}

.doc-header {
  margin-bottom: var(--forte-space-2);
}

.doc-title {
  font-size: var(--forte-text-sm);
  font-weight: var(--forte-font-medium);
  color: var(--forte-text-secondary);
  margin: 0 0 var(--forte-space-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-date {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  margin: 0 0 var(--forte-space-2);
}

.doc-actions {
  display: flex;
  gap: var(--forte-space-2);
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
}

.session-item {
  padding: var(--forte-space-3);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
  cursor: pointer;
  transition: all var(--forte-transition-fast);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--forte-space-2);
}

.session-item:hover {
  background: var(--forte-primary-lighter);
  transform: translateX(4px);
}

.session-item.active {
  background: var(--forte-primary-lighter);
  border-left: 3px solid var(--forte-primary);
}

.session-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.session-actions {
  display: flex;
  gap: var(--forte-space-1);
  flex-shrink: 0;
}

.session-actions .el-button {
  opacity: 0;
  transition: opacity var(--forte-transition-fast);
}

.session-item:hover .session-actions .el-button {
  opacity: 1;
}

.session-id {
  font-size: var(--forte-text-sm);
  font-weight: var(--forte-font-medium);
  color: white;
  margin-bottom: var(--forte-space-1);
}

.session-meta {
  font-size: var(--forte-text-xs);
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Стили для диалога сводки */
:deep(.summary-dialog) {
  width: 600px;
  max-width: 90vw;
  background-color: var(--forte-bg-primary);
}

:deep(.summary-dialog .el-message-box__message) {
  max-height: 70vh;
  overflow-y: auto;
  background-color: var(--forte-bg-primary);

}
</style>