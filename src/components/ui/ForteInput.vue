<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: false
  },
  maxlength: {
    type: Number,
    default: null
  },
  showCount: {
    type: Boolean,
    default: false
  },
  prefix: {
    type: Object,
    default: null
  },
  suffix: {
    type: Object,
    default: null
  },
  size: {
    type: String,
    default: 'default'
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur'])

const inputRef = ref(null)
const isFocused = ref(false)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
    emit('change', value)
  }
})

const charCount = computed(() => {
  return String(props.modelValue).length
})

const showClear = computed(() => {
  return props.clearable && inputValue.value && !props.disabled && !props.readonly
})

function handleClear() {
  inputValue.value = ''
  inputRef.value?.focus()
}

function handleFocus(event) {
  isFocused.value = true
  emit('focus', event)
}

function handleBlur(event) {
  isFocused.value = false
  emit('blur', event)
}
</script>

<template>
  <div
    :class="[
      'forte-input',
      `forte-input-${size}`,
      {
        'forte-input-focused': isFocused,
        'forte-input-disabled': disabled
      }
    ]"
  >
    <el-icon v-if="prefix" class="input-prefix">
      <component :is="prefix" />
    </el-icon>
    
    <input
      ref="inputRef"
      v-model="inputValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :maxlength="maxlength"
      class="input-element"
      @focus="handleFocus"
      @blur="handleBlur"
    />
    
    <el-icon
      v-if="showClear"
      class="input-clear"
      @click="handleClear"
    >
      <CircleClose />
    </el-icon>
    
    <el-icon v-else-if="suffix" class="input-suffix">
      <component :is="suffix" />
    </el-icon>
    
    <span v-if="showCount && maxlength" class="input-count">
      {{ charCount }} / {{ maxlength }}
    </span>
  </div>
</template>

<style scoped>
.forte-input {
  display: flex;
  align-items: center;
  gap: var(--forte-space-2);
  background: white;
  border: 1px solid var(--forte-border-medium);
  border-radius: var(--forte-radius-md);
  transition: all var(--forte-transition-fast);
}

.forte-input:hover:not(.forte-input-disabled) {
  border-color: var(--forte-primary-light);
}

.forte-input-focused {
  border-color: var(--forte-primary);
  box-shadow: 0 0 0 2px var(--forte-primary-lighter);
}

.forte-input-disabled {
  background: var(--forte-bg-secondary);
  cursor: not-allowed;
}

/* Sizes */
.forte-input-small {
  padding: var(--forte-space-2) var(--forte-space-3);
  font-size: var(--forte-text-sm);
}

.forte-input-default {
  padding: var(--forte-space-3) var(--forte-space-4);
  font-size: var(--forte-text-base);
}

.forte-input-large {
  padding: var(--forte-space-4) var(--forte-space-5);
  font-size: var(--forte-text-lg);
}

.input-element {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--forte-font-family);
  color: var(--forte-text-primary);
}

.input-element::placeholder {
  color: var(--forte-text-disabled);
}

.input-element:disabled {
  cursor: not-allowed;
}

.input-prefix,
.input-suffix {
  color: var(--forte-text-secondary);
  flex-shrink: 0;
}

.input-clear {
  color: var(--forte-text-secondary);
  cursor: pointer;
  flex-shrink: 0;
}

.input-clear:hover {
  color: var(--forte-text-primary);
}

.input-count {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}
</style>