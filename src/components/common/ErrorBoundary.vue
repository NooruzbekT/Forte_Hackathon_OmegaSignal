<script setup>
import { ref, onErrorCaptured } from 'vue'
import { Warning } from '@element-plus/icons-vue'

const hasError = ref(false)
const errorMessage = ref('')
const errorStack = ref('')

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message
  errorStack.value = err.stack
  
  console.error('Error caught by boundary:', err)
  console.error('Error info:', info)
  
  return false
})

function handleReload() {
  window.location.reload()
}

function handleReset() {
  hasError.value = false
  errorMessage.value = ''
  errorStack.value = ''
}
</script>

<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <el-icon :size="80" color="var(--forte-error)">
        <Warning />
      </el-icon>
      
      <h2 class="error-title">Что-то пошло не так</h2>
      
      <p class="error-message">{{ errorMessage }}</p>
      
      <details class="error-details">
        <summary>Детали ошибки</summary>
        <pre class="error-stack">{{ errorStack }}</pre>
      </details>
      
      <div class="error-actions">
        <el-button type="primary" @click="handleReload">
          Перезагрузить страницу
        </el-button>
        <el-button @click="handleReset">
          Попробовать снова
        </el-button>
      </div>
    </div>
  </div>
  
  <slot v-else />
</template>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--forte-space-6);
  background: var(--forte-bg-secondary);
}

.error-content {
  max-width: 600px;
  text-align: center;
  background: white;
  padding: var(--forte-space-12);
  border-radius: var(--forte-radius-lg);
  box-shadow: var(--forte-shadow-lg);
}

.error-title {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin: var(--forte-space-4) 0;
}

.error-message {
  font-size: var(--forte-text-base);
  color: var(--forte-text-secondary);
  margin-bottom: var(--forte-space-6);
}

.error-details {
  text-align: left;
  margin-bottom: var(--forte-space-6);
  padding: var(--forte-space-4);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
}

.error-details summary {
  cursor: pointer;
  font-weight: var(--forte-font-medium);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-3);
}

.error-stack {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-actions {
  display: flex;
  gap: var(--forte-space-3);
  justify-content: center;
}
</style>