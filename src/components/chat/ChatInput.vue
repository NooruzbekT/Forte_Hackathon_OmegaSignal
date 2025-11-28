<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Position } from '@element-plus/icons-vue'

const emit = defineEmits(['send'])

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: 'Опишите требования к проекту...'
  },
  maxLength: {
    type: Number,
    default: 2000
  }
})

const inputText = ref('')
const isComposing = ref(false)

const charCount = computed(() => inputText.value.length)
const canSend = computed(() => {
  return inputText.value.trim().length > 0 && 
         !props.disabled && 
         charCount.value <= props.maxLength
})

function handleSend() {
  if (!canSend.value) return
  
  const message = inputText.value.trim()
  emit('send', message)
  inputText.value = ''
}

function handleKeydown(event) {
  if (props.disabled) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
    }
    return
  }
  
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handlePaste(event) {
  const pastedText = event.clipboardData?.getData('text')
  if (pastedText && (charCount.value + pastedText.length) > props.maxLength) {
    ElMessage.warning(`Максимальная длина сообщения: ${props.maxLength} символов`)
  }
}
</script>

<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <el-input
        v-model="inputText"
        type="textarea"
        :placeholder="disabled ? 'AI генерирует ответ...' : 'Опишите требования к проекту...'"
        :disabled="disabled"
        :autosize="{ minRows: 1, maxRows: 6 }"
        resize="none"
        class="chat-textarea"
        @keydown="handleKeydown"
      />

      <el-button
        type="primary"
        :icon="Position"
        :disabled="!canSend || disabled"
        :loading="disabled"
        @click="handleSend"
        circle
        class="send-button"
      />
    </div>

    <div class="input-helper">
      <span v-if="disabled" class="helper-text processing">
        ⏳ AI обрабатывает ваш запрос...
      </span>
      <span v-else class="helper-text">
        Нажмите Enter для отправки, Shift+Enter для новой строки
      </span>
    </div>
  </div>
</template>

<style scoped>
.chat-input-container {
  background: var(--forte-bg-primary);
  border-top: 1px solid var(--forte-border-light);
  padding: var(--forte-space-4) var(--forte-space-6);
  flex-shrink: 0;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--forte-space-3);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-lg);
  padding: var(--forte-space-3);
  border: 2px solid transparent;
  transition: border-color var(--forte-transition-fast);
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
.input-wrapper:focus-within {
  border-color: var(--forte-primary);
}

.chat-textarea {
  flex: 1;
}

.chat-textarea :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: var(--forte-space-2);
  font-size: var(--forte-text-base);
  line-height: 1.5;
  color: white;
}

.chat-textarea :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: var(--forte-space-2);
}

.char-counter {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  transition: color var(--forte-transition-fast);
}

.char-counter-warning {
  color: var(--forte-warning);
  font-weight: var(--forte-font-semibold);
}

.send-button {
  width: 40px;
  height: 40px;
  transition: all var(--forte-transition-base);
  background: var(--forte-primary-light);
  border: none
}

.send-button:not(:disabled):hover {
  transform: scale(1.1);
}

.input-helper {
  margin-top: var(--forte-space-3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.helper-text {
  display: flex;
  align-items: center;
  gap: var(--forte-space-2);
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .chat-input-container {
    padding: var(--forte-space-3) var(--forte-space-4);
  }
  
  .helper-text {
    display: none;
  }
}

.helper-text.processing {
  color: var(--forte-primary);
  font-weight: var(--forte-font-medium);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.chat-textarea :deep(.el-textarea__inner:disabled) {
  background: var(--forte-bg-secondary);
  color: var(--forte-text-primary);
  cursor: not-allowed;
}

.input-wrapper:has(.el-textarea.is-disabled) {
  border-color: var(--forte-border-light);
  opacity: 0.7;
}
</style>