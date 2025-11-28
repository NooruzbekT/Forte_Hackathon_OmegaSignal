<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import { useLayerStore } from '@/stores/layerStore'
import { useDocumentStore } from '@/stores/documentStore'
import { useChat } from '@/composables/useChat'
import { wsManager } from '@/utils/api/websocket'
import { ElMessage } from 'element-plus'
import { Plus, ArrowDown } from '@element-plus/icons-vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import TypingIndicator from './TypingIndicator.vue'
import WelcomeScreen from './WelcomeScreen.vue'
import LayerProgress from '@/components/layers/LayerProgress.vue'

const chatStore = useChatStore()
const layerStore = useLayerStore()

const messagesContainer = ref(null)
const isScrolledToBottom = ref(true)

const messages = computed(() => chatStore.messages)
const hasMessages = computed(() => messages.value.length > 0)
const currentLayer = computed(() => layerStore.currentLayer)

const { sendMessage, isLoading } = useChat()
const { connectWebSocket } = useChat()

async function handleSendMessage(content) {
  if (!content.trim()) {
    ElMessage.warning('Пожалуйста, введите сообщение')
    return
  }

  try {
    await sendMessage(content)
    await nextTick()
    if (isScrolledToBottom.value) {
      scrollToBottom()
    }
  } catch (error) {
    ElMessage.error('Ошибка отправки сообщения')
    console.error(error)
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function handleScroll() {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const threshold = 100
  isScrolledToBottom.value = scrollHeight - scrollTop - clientHeight < threshold
}

function handleNewChat() {
  chatStore.startNewSession()
  layerStore.reset()
}

onMounted(async () => {
  scrollToBottom()
    await nextTick()
  
  console.log('SessionId:', chatStore.currentSessionId)
  
  const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
  if (!USE_MOCK) {
    try {
      await connectWebSocket()
    } catch (err) {
      console.error('WebSocket connection failed:', err)
    }
  }
})

onUnmounted(() => {
  wsManager.disconnect()
})

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    if (isScrolledToBottom.value) {
      scrollToBottom()
    }
  }
)
</script>

<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="chat-header-content">
        <h1 class="chat-title">
          AI Business Analyst
        </h1>
        
        <el-button 
          type="primary" 
          color="#1464a5"
          :icon="Plus"
          @click="handleNewChat"
          v-if="hasMessages"
        >
          Новый чат
        </el-button>
      </div>
      
      <LayerProgress 
        v-if="hasMessages"
        :current-layer="currentLayer"
        class="layer-progress-bar"
      />
    </div>

    <div 
      ref="messagesContainer"
      class="messages-area"
      @scroll="handleScroll"
    >
    <WelcomeScreen 
      v-if="!hasMessages" 
      @select="handleSendMessage"
    />
    <TransitionGroup name="message-list" tag="div">
      <ChatMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />
    </TransitionGroup>

      <TypingIndicator v-if="isLoading" />

      <Transition name="fade">
        <el-button
          v-show="!isScrolledToBottom && hasMessages"
          class="scroll-to-bottom"
          circle
          :icon="ArrowDown"
          @click="scrollToBottom"
        />
      </Transition>
    </div>

    <ChatInput 
      @send="handleSendMessage"
      :disabled="isLoading"
    />
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: var(--forte-bg-secondary);
}

.chat-header {
  background: var(--forte-bg-primary);
  border-bottom: 1px solid var(--forte-border-light);
  padding: var(--forte-space-4) var(--forte-space-6);
  flex-shrink: 0;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--forte-space-6);
  scroll-behavior: smooth;
  position: relative;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--forte-space-4);
}

.chat-title {
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin: 0;
}

.layer-progress-bar {
  margin-top: var(--forte-space-4);
}


.messages-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
  background: var(--forte-border-medium);
  border-radius: var(--forte-radius-full);
}

.scroll-to-bottom {
  position: fixed;
  bottom: 120px;
  right: var(--forte-space-6);
  box-shadow: var(--forte-shadow-lg);
  z-index: 10;
}

/* Animations */
.message-list-enter-active {
  transition: all 0.3s ease-out;
}

.message-list-leave-active {
  transition: all 0.2s ease-in;
}

.message-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-list-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .chat-header {
    padding: var(--forte-space-3) var(--forte-space-4);
  }
  
  .chat-title {
    font-size: var(--forte-text-xl);
  }
  
  .messages-area {
    padding: var(--forte-space-4);
  }
}
</style>