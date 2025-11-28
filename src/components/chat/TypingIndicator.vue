<script setup>
import { Service } from '@element-plus/icons-vue'
</script>

<template>
  <div class="typing-indicator">
    <el-avatar 
      :size="40"
      style="background: var(--forte-primary)"
    >
      <el-icon :size="20">
        <Service />
      </el-icon>
    </el-avatar>
    
    <div class="typing-content">
      <span class="typing-author">AI-аналитик</span>
      <div class="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: flex-start;
  gap: var(--forte-space-3);
  margin-bottom: var(--forte-space-6);
  animation: fadeIn 0.3s ease;
}

.typing-content {
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-2);
}

.typing-author {
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-base);
  color: var(--forte-text-primary);
}

.typing-dots {
  display: flex;
  gap: 6px;
  padding: var(--forte-space-3);
  background: var(--forte-primary-lighter);
  border-radius: var(--forte-radius-md);
  width: fit-content;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--forte-primary);
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>