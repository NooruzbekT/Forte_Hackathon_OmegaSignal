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
  dot: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <span
    :class="[
      'forte-badge',
      `forte-badge-${type}`,
      `forte-badge-${size}`,
      { 'forte-badge-dot': dot }
    ]"
  >
    <slot />
  </span>
</template>

<style scoped>
.forte-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--forte-space-1) var(--forte-space-2);
  border-radius: var(--forte-radius-sm);
  font-size: var(--forte-text-xs);
  font-weight: var(--forte-font-medium);
  line-height: 1;
  white-space: nowrap;
}

/* Sizes */
.forte-badge-small {
  padding: 2px var(--forte-space-1);
  font-size: 10px;
}

.forte-badge-default {
  padding: var(--forte-space-1) var(--forte-space-2);
  font-size: var(--forte-text-xs);
}

.forte-badge-large {
  padding: var(--forte-space-2) var(--forte-space-3);
  font-size: var(--forte-text-sm);
}

/* Types */
.forte-badge-default {
  background: var(--forte-bg-tertiary);
  color: var(--forte-text-primary);
}

.forte-badge-primary {
  background: var(--forte-primary);
  color: white;
}

.forte-badge-success {
  background: var(--forte-success);
  color: white;
}

.forte-badge-warning {
  background: var(--forte-warning);
  color: white;
}

.forte-badge-danger {
  background: var(--forte-error);
  color: white;
}

.forte-badge-info {
  background: var(--forte-info);
  color: white;
}

/* Dot variant */
.forte-badge-dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border-radius: 50%;
}

.forte-badge-dot.forte-badge-large {
  width: 10px;
  height: 10px;
}
</style>