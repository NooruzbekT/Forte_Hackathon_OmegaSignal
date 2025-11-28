<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: {
    type: Number,
    required: true
  },
  total: {
    type: Number,
    required: true
  },
  steps: {
    type: Array,
    default: () => []
  }
})

const progress = computed(() => {
  return (props.current / props.total) * 100
})
</script>

<template>
  <div class="form-progress">
    <div class="progress-header">
      <span class="progress-text">
        Шаг {{ current }} из {{ total }}
      </span>
      <span class="progress-percent">
        {{ Math.round(progress) }}%
      </span>
    </div>
    
    <el-progress
      :percentage="progress"
      :show-text="false"
      :stroke-width="8"
      color="var(--forte-primary)"
    />
    
    <div v-if="steps.length > 0" class="progress-steps">
      <div
        v-for="(step, index) in steps"
        :key="index"
        :class="[
          'step-item',
          {
            'step-active': index + 1 === current,
            'step-completed': index + 1 < current
          }
        ]"
      >
        <div class="step-marker">
          <el-icon v-if="index + 1 < current">
            <Check />
          </el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <span class="step-label">{{ step }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-progress {
  margin-bottom: var(--forte-space-6);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-3);
}

.progress-text {
  font-size: var(--forte-text-sm);
  font-weight: var(--forte-font-medium);
  color: var(--forte-text-primary);
}

.progress-percent {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: var(--forte-space-6);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--forte-space-2);
  flex: 1;
}

.step-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--forte-bg-secondary);
  border: 2px solid var(--forte-border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  transition: all var(--forte-transition-base);
}

.step-active .step-marker {
  background: var(--forte-primary);
  border-color: var(--forte-primary);
  color: white;
}

.step-completed .step-marker {
  background: var(--forte-success);
  border-color: var(--forte-success);
  color: white;
}

.step-label {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  text-align: center;
}

.step-active .step-label {
  color: var(--forte-text-primary);
  font-weight: var(--forte-font-medium);
}
</style>