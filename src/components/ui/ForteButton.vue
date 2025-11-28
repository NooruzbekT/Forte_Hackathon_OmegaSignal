<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  size: {
    type: String,
    default: 'default'
  },
  icon: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

function handleClick(event) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<template>
  <button
    :class="[
      'forte-button',
      `forte-button-${type}`,
      `forte-button-${size}`,
      { 
        'forte-button-block': block,
        'forte-button-loading': loading,
        'forte-button-disabled': disabled
      }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <el-icon v-if="loading" class="button-loading-icon">
      <Loading />
    </el-icon>
    <el-icon v-else-if="icon" class="button-icon">
      <component :is="icon" />
    </el-icon>
    <span class="button-text">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.forte-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--forte-space-2);
  font-family: var(--forte-font-family);
  font-weight: var(--forte-font-medium);
  border: 1px solid transparent;
  border-radius: var(--forte-radius-md);
  cursor: pointer;
  transition: all var(--forte-transition-fast);
  outline: none;
}

/* Sizes */
.forte-button-small {
  padding: var(--forte-space-2) var(--forte-space-3);
  font-size: var(--forte-text-sm);
}

.forte-button-default {
  padding: var(--forte-space-3) var(--forte-space-4);
  font-size: var(--forte-text-base);
}

.forte-button-large {
  padding: var(--forte-space-4) var(--forte-space-6);
  font-size: var(--forte-text-lg);
}

/* Types */
.forte-button-default {
  background: white;
  border-color: var(--forte-border-medium);
  color: var(--forte-text-primary);
}

.forte-button-default:hover:not(:disabled) {
  border-color: var(--forte-primary);
  color: var(--forte-primary);
}

.forte-button-primary {
  background: var(--forte-primary);
  color: white;
}

.forte-button-primary:hover:not(:disabled) {
  background: var(--forte-primary-dark);
  box-shadow: var(--forte-shadow-primary);
}

.forte-button-success {
  background: var(--forte-success);
  color: white;
}

.forte-button-success:hover:not(:disabled) {
  opacity: 0.9;
}

.forte-button-danger {
  background: var(--forte-error);
  color: white;
}

.forte-button-danger:hover:not(:disabled) {
  opacity: 0.9;
}

/* States */
.forte-button-block {
  width: 100%;
}

.forte-button-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.forte-button-loading {
  cursor: wait;
}

.button-loading-icon {
  animation: spin 1s linear infinite;
}
</style>