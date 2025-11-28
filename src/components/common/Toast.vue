<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info'
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const visible = ref(false)

const iconMap = {
  success: 'SuccessFilled',
  warning: 'WarningFilled',
  error: 'CircleCloseFilled',
  info: 'InfoFilled'
}

const icon = computed(() => iconMap[props.type])

function show() {
  visible.value = true
  
  if (props.duration > 0) {
    setTimeout(() => {
      hide()
    }, props.duration)
  }
}

function hide() {
  visible.value = false
}

defineExpose({ show, hide })
</script>

<template>
  <Transition name="toast">
    <div
      v-if="visible"
      :class="['toast', `toast-${type}`]"
      @click="hide"
    >
      <el-icon :size="20" class="toast-icon">
        <component :is="icon" />
      </el-icon>
      <span class="toast-message">{{ message }}</span>
    </div>
  </Transition>
</template>

<style scoped>
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  padding: var(--forte-space-4) var(--forte-space-5);
  background: white;
  border-radius: var(--forte-radius-md);
  box-shadow: var(--forte-shadow-lg);
  cursor: pointer;
  z-index: 9999;
  min-width: 300px;
}

.toast-success {
  border-left: 4px solid var(--forte-success);
}

.toast-success .toast-icon {
  color: var(--forte-success);
}

.toast-warning {
  border-left: 4px solid var(--forte-warning);
}

.toast-warning .toast-icon {
  color: var(--forte-warning);
}

.toast-error {
  border-left: 4px solid var(--forte-error);
}

.toast-error .toast-icon {
  color: var(--forte-error);
}

.toast-info {
  border-left: 4px solid var(--forte-info);
}

.toast-info .toast-icon {
  color: var(--forte-info);
}

.toast-message {
  flex: 1;
  font-size: var(--forte-text-sm);
  color: var(--forte-text-primary);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>