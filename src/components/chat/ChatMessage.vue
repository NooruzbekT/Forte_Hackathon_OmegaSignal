<script setup>
import { computed } from 'vue'
import { User, Service } from '@element-plus/icons-vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')
const hasLayer = computed(() => props.message.layer !== null)

const layerNames = {
  1: { name: 'Intent Understanding', color: '#9C27B0' },
  2: { name: 'Requirement Gathering', color: '#2196F3' },
  3: { name: 'RAG Search', color: '#FF9800' },
  4: { name: 'Document Generation', color: '#00A651' },
  5: { name: 'Quality Validation', color: '#4CAF50' }
}

const layerInfo = computed(() => {
  return hasLayer.value ? layerNames[props.message.layer] : null
})

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div 
    :class="[
      'chat-message',
      { 'message-user': isUser, 'message-assistant': isAssistant }
    ]"
  >
    <div class="message-header">
      <el-avatar 
        :size="40"
        :style="{ 
          background: isUser ? 'var(--forte-border-medium)' : 'var(--forte-primary-lighter)' 
        }"
      >
        <el-icon :size="20">
          <User v-if="isUser" />
          <Service v-else />
        </el-icon>
      </el-avatar>

      <div class="message-meta">
        <span class="message-author">
          {{ isUser ? 'Вы' : 'AI-аналитик' }}
        </span>
        
        <el-tag 
          v-if="layerInfo"
          :color="layerInfo.color"
          size="small"
          effect="dark"
          class="layer-tag"
        >
          Layer {{ message.layer }}: {{ layerInfo.name }}
        </el-tag>
      </div>

      <span class="message-time">
        {{ formatTime(message.timestamp) }}
      </span>
    </div>

    <div class="message-body">
      <div class="message-content">
        {{ message.content }}
      </div>
      
      <div v-if="message.document" class="message-document">
        <el-card shadow="hover">
          <div class="document-badge">
            <el-tag type="success">{{ message.document.type }}</el-tag>
            <span>Документ сгенерирован</span>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  margin-bottom: var(--forte-space-6);
  animation: slideIn 0.3s ease-out;
}

.message-header {
  display: flex;
  align-items: flex-start;
  gap: var(--forte-space-3);
  margin-bottom: var(--forte-space-4);
}

.message-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
}

.message-author {
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-base);
  color: var(--forte-text-primary);
}

.layer-tag {
  width: fit-content;
}

.message-time {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
  white-space: nowrap;
}

.message-body {
  margin-left: calc(40px + var(--forte-space-3));
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
}

.message-content {
  padding: var(--forte-space-4);
  border-radius: var(--forte-radius-md);
  line-height: 1.6;
  color: var(--forte-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-user .message-content {
  background: var(--forte-border-medium);
  border: 1px solid var(--forte-border-light);
}

.message-assistant .message-content {
  background: var(--forte-primary-lighter);
}

.message-document {
  margin-top: var(--forte-space-3);
}

.document-badge {
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  font-size: var(--forte-text-sm);
  color: var(--forte-text-primary);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .message-body {
    margin-left: 0;
    margin-top: var(--forte-space-3);
  }
}
</style>