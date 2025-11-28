<script setup>
import { computed } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import ChatHistory from '@/components/chat/ChatHistory.vue'

const chatStore = useChatStore()
const messages = computed(() => chatStore.messages)
</script>

<template>
  <div class="history-view">
    <div class="view-header">
      <h1>История чатов</h1>
      <el-tag type="info">{{ messages.length }} сообщений</el-tag>
    </div>
    
    <ChatHistory :messages="messages" />
  </div>
</template>

<style scoped>
.history-view {
  padding: var(--forte-space-6);
  height: 100%;
  overflow-y: auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-6);
}

.view-header h1 {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  margin: 0;
}
</style>