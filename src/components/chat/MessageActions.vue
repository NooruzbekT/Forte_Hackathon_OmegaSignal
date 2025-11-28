<script setup>
import { CopyDocument, RefreshRight } from '@element-plus/icons-vue'
import { useClipboard } from '@/composables/useClipboard'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['regenerate'])

const { copy } = useClipboard()

function handleCopy() {
  copy(props.message.content)
}

function handleRegenerate() {
  emit('regenerate', props.message.id)
}
</script>

<template>
  <div class="message-actions">
    <el-button
      size="small"
      :icon="CopyDocument"
      @click="handleCopy"
      text
    >
      Копировать
    </el-button>
    
    <el-button
      v-if="message.role === 'assistant'"
      size="small"
      :icon="RefreshRight"
      @click="handleRegenerate"
      text
    >
      Регенерировать
    </el-button>
  </div>
</template>

<style scoped>
.message-actions {
  display: flex;
  gap: var(--forte-space-2);
  margin-top: var(--forte-space-3);
  opacity: 0;
  transition: opacity var(--forte-transition-fast);
}

.message-actions:hover,
.message-content:hover + .message-actions {
  opacity: 1;
}
</style>