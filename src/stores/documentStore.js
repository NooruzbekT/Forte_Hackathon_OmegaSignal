// src/stores/documentStore.js
import { defineStore } from 'pinia'
import axios from 'axios'

// Создаём базовый API клиент
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const useDocumentStore = defineStore('documents', {
  state: () => ({
    documents: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    // Геттер для получения количества документов
    documentCount: (state) => state.documents.length,
    
    // Геттер для получения документов по типу
    documentsByType: (state) => (type) => {
      return state.documents.filter(doc => doc.type === type)
    }
  },

  actions: {
    addDocument(doc) {
      if (!doc) return
      const id = doc.id || doc.filename
      if (!id) return

      const idx = this.documents.findIndex(d => (d.id || d.filename) === id)
      if (idx !== -1) {
        // Обновляем существующий документ
        this.documents[idx] = { ...this.documents[idx], ...doc }
      } else {
        // Добавляем новый документ в начало списка
        this.documents.unshift(doc)
      }
    },

    removeDocument(filename) {
      this.documents = this.documents.filter(
        d => d.filename !== filename && d.id !== filename
      )
    },

    clear() {
      this.documents = []
      this.error = null
    },

    async fetchAllDocuments() {
      this.isLoading = true
      this.error = null

      try {
        console.log('Загрузка документов с бэкенда...')
        
        const response = await apiClient.get('/api/documents')
        const docs = response.data || []

        console.log('Получено документов:', docs.length)

        // Маппим данные с бэкенда в формат фронта
        this.documents = docs.map(d => {
          // Определяем тип документа
          let type = d.doc_type || 'DOC'
          
          // Если doc_type не пришёл с бэка, пытаемся определить по имени файла
          if (!d.doc_type) {
            const lower = (d.filename || '').toLowerCase()
            if (lower.includes('business_requirements') || lower.includes('brd')) {
              type = 'BRD'
            } else if (lower.includes('integration')) {
              type = 'INTEGRATION'
            } else if (lower.includes('bug')) {
              type = 'BUG_FIX'
            } else if (lower.includes('process')) {
              type = 'PROCESS_CHANGE'
            } else if (lower.includes('data')) {
              type = 'DATA_REQUEST'
            }
          }

          return {
            id: d.filename,              // внутренний id в сторе
            filename: d.filename,        // нужен для download/delete
            document_path: d.path,       // путь на диске
            type,                        // тип документа для тегов
            title: d.filename || 'Document',
            sessionId: d.session_id || null,
            status: 'ready',
            createdAt: d.created,        // ISO-строка
            size: d.size,
            url: d.url || `/api/documents/${d.filename}`, // URL для скачивания
          }
        })

        console.log('Документы успешно загружены:', this.documents)

      } catch (error) {
        console.error('Ошибка загрузки документов:', error)
        this.error = error.response?.data?.message || error.message || 'Ошибка загрузки документов'
        
        // Показываем более детальную информацию об ошибке
        if (error.response) {
          console.error('Response error:', error.response.status, error.response.data)
        } else if (error.request) {
          console.error('Request error:', error.request)
        }
      } finally {
        this.isLoading = false
      }
    },

    async deleteDocument(filename) {
      try {
        console.log('Удаление документа:', filename)
        await apiClient.delete(`/api/documents/${filename}`)
        
        // Удаляем из локального стора
        this.removeDocument(filename)
        
        console.log('Документ успешно удалён')
        return true
      } catch (error) {
        console.error('Ошибка удаления документа:', error)
        this.error = error.response?.data?.message || 'Ошибка удаления документа'
        throw error
      }
    },

    async downloadDocument(filename) {
      try {
        console.log('Скачивание документа:', filename)
        
        const response = await apiClient.get(`/api/documents/${filename}`, {
          responseType: 'blob'
        })
        
        // Создаём ссылку для скачивания
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        console.log('Документ успешно скачан')
        return true
      } catch (error) {
        console.error('Ошибка скачивания документа:', error)
        this.error = error.response?.data?.message || 'Ошибка скачивания документа'
        throw error
      }
    }
  },
})