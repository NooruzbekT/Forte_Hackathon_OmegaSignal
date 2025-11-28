<script setup>
import { computed } from 'vue'
import { formatDate } from '@/utils/formatters/dateFormatter'

const props = defineProps({
  document: {
    type: Object,
    required: true
  }
})

const documentType = computed(() => {
  const types = {
    BRD: { color: 'success', label: 'Business Requirements Document' },
    PRD: { color: 'primary', label: 'Product Requirements Document' },
    TSD: { color: 'warning', label: 'Technical Specification Document' }
  }
  return types[props.document.type] || types.BRD
})
</script>

<template>
  <div class="document-header">
    <div class="header-top">
      <el-tag :type="documentType.color" size="large">
        {{ props.document.type }}
      </el-tag>
      <span class="document-id">ID: {{ document.id }}</span>
    </div>
    
    <h1 class="document-title">{{ document.title }}</h1>
    
    <p class="document-subtitle">{{ documentType.label }}</p>
    
    <div class="header-meta">
      <div class="meta-item">
        <span class="meta-label">Создан:</span>
        <span class="meta-value">{{ formatDate(document.createdAt) }}</span>
      </div>
      
      <div class="meta-item">
        <span class="meta-label">Обновлен:</span>
        <span class="meta-value">{{ formatDate(document.updatedAt) }}</span>
      </div>
      
      <div v-if="document.author" class="meta-item">
        <span class="meta-label">Автор:</span>
        <span class="meta-value">{{ document.author }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.document-header {
  padding: var(--forte-space-6);
  background: white;
  border-bottom: 1px solid var(--forte-border-light);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-4);
}

.document-id {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  font-family: monospace;
}

.document-title {
  font-size: var(--forte-text-3xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin: 0 0 var(--forte-space-2);
}

.document-subtitle {
  font-size: var(--forte-text-lg);
  color: var(--forte-text-secondary);
  margin: 0 0 var(--forte-space-6);
}

.header-meta {
  display: flex;
  gap: var(--forte-space-6);
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  gap: var(--forte-space-2);
  font-size: var(--forte-text-sm);
}

.meta-label {
  color: var(--forte-text-secondary);
  font-weight: var(--forte-font-medium);
}

.meta-value {
  color: var(--forte-text-primary);
}
</style>