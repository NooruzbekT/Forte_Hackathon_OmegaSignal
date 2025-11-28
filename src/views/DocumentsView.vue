<script setup>
import { computed } from 'vue'
import { useDocumentStore } from '@/stores/documentStore'
import DocumentList from '@/components/documents/DocumentList.vue'

const documentStore = useDocumentStore()
const documents = computed(() => documentStore.documents)
</script>

<template>
  <div class="documents-view">
    <div class="view-header">
      <h1>Документы</h1>
      <el-tag type="info">{{ documents.length }} документов</el-tag>
    </div>
    
    <DocumentList :documents="documents" />
  </div>
</template>

<style scoped>
.documents-view {
  padding: var(--forte-space-6);
  height: 100%;
  overflow-y: auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-6);
}

.view-header h1 {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  margin: 0;
}
</style>