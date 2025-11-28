import { ref } from 'vue'
import { generateDOCX } from '@/utils/generators/docxGenerator'
import { generatePDF } from '@/utils/generators/pdfGenerator'
import { useNotification } from './useNotification'

export function useExport() {
  const isExporting = ref(false)
  const { success, error } = useNotification()

  async function exportDocument(document, format) {
    isExporting.value = true

    try {
      switch (format.toLowerCase()) {
        case 'docx':
          await generateDOCX(document)
          success('DOCX файл успешно экспортирован')
          break
        case 'pdf':
          generatePDF(document)
          success('PDF файл успешно экспортирован')
          break
        default:
          throw new Error('Unsupported format')
      }
    } catch (err) {
      error('Ошибка при экспорте документа')
      console.error(err)
    } finally {
      isExporting.value = false
    }
  }

  return {
    isExporting,
    exportDocument
  }
}