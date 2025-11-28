<script setup>
import { computed } from 'vue'
import QualityBadge from './QualityBadge.vue'

const props = defineProps({
  document: {
    type: Object,
    required: true
  }
})

const metadata = computed(() => {
  return [
    { label: 'Тип', value: props.document.type },
    { label: 'Статус', value: props.document.status || 'Готов' },
    { label: 'Версия', value: props.document.version || '1.0' },
    { label: 'Язык', value: props.document.language || 'Русский' }
  ]
})

const stats = computed(() => {
  return [
    { 
      label: 'Требования', 
      value: props.document.requirements?.length || 0 
    },
    { 
      label: 'Страницы', 
      value: props.document.pages || 1 
    },
    { 
      label: 'Слова', 
      value: props.document.wordCount || 0 
    }
  ]
})
</script>

<template>
  <div class="document-metadata">
    <div class="metadata-section">
      <h3 class="section-title">Метаданные</h3>
      
      <div class="metadata-grid">
        <div
          v-for="item in metadata"
          :key="item.label"
          class="metadata-item"
        >
          <span class="item-label">{{ item.label }}:</span>
          <span class="item-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="document.quality" class="metadata-section">
      <h3 class="section-title">Качество</h3>
      
      <div class="quality-metrics">
        <div class="metric-item">
          <span class="metric-label">Общее качество</span>
          <QualityBadge :quality="document.quality.overall" />
        </div>
        
        <div class="metric-item">
          <span class="metric-label">Полнота</span>
          <el-progress
            :percentage="Math.round(document.quality.completeness * 100)"
            color="var(--forte-primary)"
          />
        </div>
        
        <div class="metric-item">
          <span class="metric-label">Согласованность</span>
          <el-progress
            :percentage="Math.round(document.quality.consistency * 100)"
            color="var(--forte-success)"
          />
        </div>
      </div>
    </div>
    
    <div class="metadata-section">
      <h3 class="section-title">Статистика</h3>
      
      <div class="stats-grid">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="stat-card"
        >
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.document-metadata {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-6);
}

.metadata-section {
  background: white;
  padding: var(--forte-space-5);
  border-radius: var(--forte-radius-md);
  border: 1px solid var(--forte-border-light);
}

.section-title {
  font-size: var(--forte-text-lg);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin: 0 0 var(--forte-space-4);
}

.metadata-grid {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
}

.metadata-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--forte-space-2) 0;
  border-bottom: 1px solid var(--forte-border-light);
}

.metadata-item:last-child {
  border-bottom: none;
}

.item-label {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  font-weight: var(--forte-font-medium);
}

.item-value {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-primary);
}

.quality-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-4);
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
}

.metric-label {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  font-weight: var(--forte-font-medium);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--forte-space-3);
}

.stat-card {
  text-align: center;
  padding: var(--forte-space-4);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
}

.stat-value {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-primary);
  margin-bottom: var(--forte-space-2);
}

.stat-label {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
}
</style>