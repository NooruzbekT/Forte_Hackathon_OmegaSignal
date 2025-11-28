<script setup>
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  shadow: {
    type: String,
    default: 'default'
  },
  bordered: {
    type: Boolean,
    default: true
  },
  hoverable: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div
    :class="[
      'forte-card',
      `forte-card-shadow-${shadow}`,
      {
        'forte-card-bordered': bordered,
        'forte-card-hoverable': hoverable
      }
    ]"
  >
    <div v-if="title || $slots.header" class="forte-card-header">
      <slot name="header">
        <h3 class="forte-card-title">{{ title }}</h3>
      </slot>
    </div>
    
    <div class="forte-card-body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="forte-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.forte-card {
  background: white;
  border-radius: var(--forte-radius-lg);
  overflow: hidden;
  transition: all var(--forte-transition-base);
}

.forte-card-bordered {
  border: 1px solid var(--forte-border-light);
}

.forte-card-shadow-default {
  box-shadow: var(--forte-shadow-sm);
}

.forte-card-shadow-md {
  box-shadow: var(--forte-shadow-md);
}

.forte-card-shadow-lg {
  box-shadow: var(--forte-shadow-lg);
}

.forte-card-hoverable {
  cursor: pointer;
}

.forte-card-hoverable:hover {
  transform: translateY(-4px);
  box-shadow: var(--forte-shadow-lg);
}

.forte-card-header {
  padding: var(--forte-space-4) var(--forte-space-5);
  border-bottom: 1px solid var(--forte-border-light);
}

.forte-card-title {
  font-size: var(--forte-text-lg);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin: 0;
}

.forte-card-body {
  padding: var(--forte-space-5);
}

.forte-card-footer {
  padding: var(--forte-space-4) var(--forte-space-5);
  border-top: 1px solid var(--forte-border-light);
  background: var(--forte-bg-secondary);
}
</style>