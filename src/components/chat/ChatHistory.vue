<script setup>
import { computed } from 'vue'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

const groupedMessages = computed(() => {
  const groups = {}
  props.messages.forEach(msg => {
    const date = new Date(msg.timestamp).toLocaleDateString('ru-RU')
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(msg)
  })
  return groups
})
</script>

<template>
  <div class="chat-history">
    <el-empty 
      v-if="messages.length === 0"
      description="Нет истории сообщений"
    />
    
    <div 
      v-for="(msgs, date) in groupedMessages"
      :key="date"
      class="history-group"
    >
      <div class="date-divider">
        <span>{{ date }}</span>
      </div>
      
      <ChatMessage
        v-for="message in msgs"
        :key="message.id"
        :message="message"
      />
    </div>
  </div>
</template>

<style scoped>
.chat-history {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-4);
}

.history-group {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-4);
}

.date-divider {
  text-align: center;
  margin: var(--forte-space-4) 0;
}

.date-divider span {
  background: var(--forte-bg-secondary);
  padding: var(--forte-space-2) var(--forte-space-4);
  border-radius: var(--forte-radius-full);
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  font-weight: var(--forte-font-medium);
}
</style>