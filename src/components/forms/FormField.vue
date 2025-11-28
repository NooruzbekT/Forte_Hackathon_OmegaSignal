<script setup>
import { computed } from 'vue'
const props = defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: [String, Number, Boolean, Array],
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
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<template>
  <div class="form-field">
    <label class="field-label">
      {{ label }}
      <span v-if="required" class="field-required">*</span>
    </label>
    
    <el-input
      v-if="type === 'text' || type === 'email' || type === 'number'"
      v-model="inputValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="{ 'is-error': error }"
    />
    
    <el-input
      v-else-if="type === 'textarea'"
      v-model="inputValue"
      type="textarea"
      :placeholder="placeholder"
      :disabled="disabled"
      :autosize="{ minRows: 3, maxRows: 6 }"
      :class="{ 'is-error': error }"
    />
    
    <el-select
      v-else-if="type === 'select'"
      v-model="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="{ 'is-error': error }"
    >
      <slot name="options" />
    </el-select>
    
    <p v-if="helpText && !error" class="field-help">
      {{ helpText }}
    </p>
    
    <p v-if="error" class="field-error">
      {{ error }}
    </p>
  </div>
</template>

<style scoped>
.form-field {
  margin-bottom: var(--forte-space-5);
}

.field-label {
  display: block;
  font-size: var(--forte-text-sm);
  font-weight: var(--forte-font-medium);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-2);
}

.field-required {
  color: var(--forte-error);
  margin-left: var(--forte-space-1);
}

.field-help {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  margin-top: var(--forte-space-2);
  margin-bottom: 0;
}

.field-error {
  font-size: var(--forte-text-xs);
  color: var(--forte-error);
  margin-top: var(--forte-space-2);
  margin-bottom: 0;
}

.is-error :deep(.el-input__wrapper) {
  border-color: var(--forte-error);
}

.is-error :deep(.el-textarea__inner) {
  border-color: var(--forte-error);
}
</style>