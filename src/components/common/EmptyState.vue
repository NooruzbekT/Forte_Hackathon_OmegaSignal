<script setup>
const props = defineProps({
  icon: {
    type: Object,
    default: null
  },
  title: {
    type: String,
    default: 'Нет данных'
  },
  description: {
    type: String,
    default: ''
  },
  buttonText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['action'])
</script>

<template>
  <div class="empty-state">
    <el-icon v-if="icon" :size="80" class="empty-icon">
      <component :is="icon" />
    </el-icon>
    
    <h3 class="empty-title">{{ title }}</h3>
    
    <p v-if="description" class="empty-description">
      {{ description }}
    </p>
    
    <el-button
      v-if="buttonText"
      type="primary"
      @click="emit('action')"
    >
      {{ buttonText }}
    </el-button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--forte-space-12);
  text-align: center;
}

.empty-icon {
  color: var(--forte-text-disabled);
  margin-bottom: var(--forte-space-4);
}

.empty-title {
  font-size: var(--forte-text-xl);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-2);
}

.empty-description {
  font-size: var(--forte-text-base);
  color: var(--forte-text-secondary);
  margin-bottom: var(--forte-space-6);
  max-width: 400px;
}
</style>