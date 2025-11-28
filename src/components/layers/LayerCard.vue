<script setup>
import { computed } from 'vue'
import { Check, Loading, Clock } from '@element-plus/icons-vue'

const props = defineProps({
  layer: {
    type: Object,
    required: true
  },
  status: {
    type: String,
    default: 'pending'
  }
})

const statusConfig = computed(() => {
  const configs = {
    pending: {
      icon: Clock,
      color: 'var(--forte-text-disabled)',
      bg: 'var(--forte-bg-secondary)'
    },
    active: {
      icon: Loading,
      color: 'var(--forte-primary)',
      bg: 'var(--forte-primary-lighter)'
    },
    completed: {
      icon: Check,
      color: 'var(--forte-success)',
      bg: 'var(--forte-success-light)'
    }
  }
  return configs[props.status] || configs.pending
})
</script>

<template>
  <div :class="['layer-card', `layer-card-${status}`]">
    <div 
      class="layer-icon"
      :style="{ 
        background: statusConfig.bg,
        color: statusConfig.color 
      }"
    >
      <el-icon :size="24" :class="{ spin: status === 'active' }">
        <component :is="statusConfig.icon" />
      </el-icon>
    </div>
    
    <div class="layer-content">
      <h4 class="layer-title">{{ layer.name }}</h4>
      <p class="layer-description">{{ layer.description }}</p>
    </div>
  </div>
</template>

<style scoped>
.layer-card {
  display: flex;
  gap: var(--forte-space-4);
  padding: var(--forte-space-4);
  background: white;
  border-radius: var(--forte-radius-md);
  border: 2px solid var(--forte-border-light);
  transition: all var(--forte-transition-base);
}

.layer-card-active {
  border-color: var(--forte-primary);
  box-shadow: var(--forte-shadow-md);
}

.layer-card-completed {
  border-color: var(--forte-success);
}

.layer-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--forte-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.layer-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.layer-title {
  font-size: var(--forte-text-lg);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin: 0 0 var(--forte-space-2);
}

.layer-description {
  font-size: var(--forte-text-sm);
  color: white;
  margin: 0;
}

.spin {
  animation: spin 1s linear infinite;
}
</style>