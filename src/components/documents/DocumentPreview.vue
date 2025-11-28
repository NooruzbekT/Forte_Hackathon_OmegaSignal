<script setup>
import { computed } from 'vue'
import { Download, Delete, View } from '@element-plus/icons-vue'
import { formatDate } from '@/utils/formatters/dateFormatter'
import { useExport } from '@/composables/useExport'
import { useDocumentStore } from '@/stores/documentStore'
import QualityBadge from './QualityBadge.vue'

const props = defineProps({
  document: {
    type: Object,
    required: true
  }
})

const documentStore = useDocumentStore()
const { exportDocument } = useExport()

const documentType = computed(() => {
  const types = {
    BRD: { color: 'success', label: 'BRD' },
    PRD: { color: 'primary', label: 'PRD' },
    TSD: { color: 'warning', label: 'TSD' }
  }
  return types[props.document.type] || types.BRD
})

function handleDownload(format) {
  exportDocument(props.document, format)
}

function handleDelete() {
  documentStore.deleteDocument(props.document.id)
}

function handleView() {
  documentStore.setCurrentDocument(props.document)
}
</script>

<template>
  <el-card class="document-preview" shadow="hover">
    <div class="document-header">
      <el-tag :type="documentType.color" size="small">
        {{ documentType.label }}
      </el-tag>
      <QualityBadge
        v-if="document.quality"
        :quality="document.quality.overall"
      />
    </div>
    
    <h3 class="document-title">{{ document.title }}</h3>
    
    <p class="document-date">
      {{ formatDate(document.createdAt, 'short') }}
    </p>
    
    <div class="document-actions">
      <el-button
        size="small"
        :icon="View"
        @click="handleView"
      >
        Просмотр
      </el-button>
      
      <el-dropdown>
        <el-button size="small" :icon="Download">
          Скачать
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleDownload('docx')">
              DOCX
            </el-dropdown-item>
            <el-dropdown-item @click="handleDownload('pdf')">
              PDF
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <el-button
        size="small"
        :icon="Delete"
        type="danger"
        @click="handleDelete"
      />
    </div>
  </el-card>
</template>

<style scoped>
.document-preview {
  cursor: pointer;
  transition: all var(--forte-transition-fast);
}

.document-preview:hover {
  transform: translateY(-4px);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-3);
}

.document-title {
  font-size: var(--forte-text-lg);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-date {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  margin-bottom: var(--forte-space-4);
}

.document-actions {
  display: flex;
  gap: var(--forte-space-2);
  flex-wrap: wrap;
}
</style>