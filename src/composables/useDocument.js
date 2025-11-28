import { ref } from 'vue'
import { apiClient } from '../utils/api/client'
import { API_ENDPOINTS } from '../utils/api/endpoints'
import { useDocumentStore } from '../stores/documentStore'
import { ElMessage } from 'element-plus'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export function useDocument() {
  const documentStore = useDocumentStore()
  const isLoading = ref(false)

  // ==========================
  // 📥 СКАЧАТЬ ДОКУМЕНТ
  // ==========================
  async function downloadDocument(filename) {
    if (USE_MOCK) {
      ElMessage.info('Mock режим - скачивание недоступно')
      return
    }

    try {
      await apiClient.downloadFile(
        API_ENDPOINTS.DOCUMENT_DOWNLOAD(filename),
        filename
      )
      ElMessage.success('Документ скачан')
    } catch (err) {
      console.error('Download error:', err)
      ElMessage.error('Ошибка скачивания')
      throw err
    }
  }


  // ==========================
  // 🗑 УДАЛИТЬ ДОКУМЕНТ
  // ==========================
  async function deleteDocument(documentPath) {
    if (USE_MOCK) {
      documentStore.deleteDocument(documentPath)
      ElMessage.success('Документ удалён (mock)')
      return
    }

    if (!documentPath) {
      ElMessage.error('Документ не имеет пути')
      return
    }

    try {
      await apiClient.delete(API_ENDPOINTS.DOCUMENT_DELETE(documentPath))
      documentStore.deleteDocument(documentPath)
      ElMessage.success('Документ удалён')
    } catch (err) {
      ElMessage.error('Ошибка удаления')
      throw err
    }
  }

  // ==========================
  // 📄 ЗАГРУЗИТЬ СПИСОК ДОКОВ
  // ==========================
  async function loadDocuments() {
    if (USE_MOCK) return []

    isLoading.value = true
    try {
      const response = await apiClient.get(API_ENDPOINTS.DOCUMENTS_LIST)
      const docs = response?.documents || []

      docs.forEach(doc => documentStore.addDocument(doc))

      return docs
    } catch (err) {
      console.error('Failed to load documents:', err)
      ElMessage.error('Ошибка загрузки документов')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    downloadDocument,
    deleteDocument,
    loadDocuments
  }
}
