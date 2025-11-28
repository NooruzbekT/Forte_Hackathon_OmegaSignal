<script setup>
import { computed } from 'vue'
import DocumentPreview from './DocumentPreview.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { Document } from '@element-plus/icons-vue'

const props = defineProps({
  documents: {
    type: Array,
    default: () => []
  }
})

const isEmpty = computed(() => props.documents.length === 0)
</script>

<template>
  <div class="document-list">
    <EmptyState
      v-if="isEmpty"
      :icon="Document"
      title="Нет документов"
      description="Создайте новый документ через чат с AI-аналитиком"
    />
    
    <div v-else class="documents-grid">
      <DocumentPreview
        v-for="doc in documents"
        :key="doc.id"
        :document="doc"
      />
    </div>
  </div>
</template>

<style scoped>
.document-list {
  width: 100%;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--forte-space-4);
}
</style>