<script setup>
const props = defineProps({
  size: {
    type: String,
    default: 'default'
  },
  text: {
    type: String,
    default: 'Загрузка...'
  }
})

const sizeMap = {
  small: 24,
  default: 40,
  large: 60
}
</script>

<template>
  <div class="loading-spinner">
    <el-icon 
      :size="sizeMap[size]" 
      class="spinner-icon"
    >
      <Loading />
    </el-icon>
    <p v-if="text" class="spinner-text">{{ text }}</p>
  </div>
</template>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--forte-space-3);
  padding: var(--forte-space-6);
}

.spinner-icon {
  color: var(--forte-primary);
  animation: spin 1s linear infinite;
}

.spinner-text {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  margin: 0;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>