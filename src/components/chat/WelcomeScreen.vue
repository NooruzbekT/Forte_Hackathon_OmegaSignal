<script setup>
import { ChatDotRound } from '@element-plus/icons-vue'

const emit = defineEmits(['select'])

const suggestions = [
  {
    id: 1,
    text: 'Создать BRD для добавления QR-оплаты в мобильное приложение'
  },
  {
    id: 2,
    text: 'Подготовить PRD для интеграции с новым платежным шлюзом'
  },
  {
    id: 3,
    text: 'Создать TSD для системы управления пользователями'
  }
]

function handleSelect(text) {
  emit('select', text)
}
</script>

<template>
  <div class="welcome-screen">    
    <h2 class="welcome-title">
      Начните новый диалог с AI-аналитиком
    </h2>
    
    <p class="welcome-description">
      Опишите ваши требования к проекту, и я помогу создать
      профессиональную бизнес-документацию
    </p>
    
    <div class="welcome-suggestions">
      <p class="suggestions-title">Примеры запросов:</p>
      <el-button
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        @click="handleSelect(suggestion.text)"
        class="suggestion-button"
        plain
        background="var(--forte-bg-secondary)"
      >
        {{ suggestion.text }}
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--forte-space-12);
  max-width: 700px;
  margin: 0 auto;
  min-height: 60vh;
  width: 100%;
}

.welcome-icon {
  margin-bottom: var(--forte-space-6);
  opacity: 0.9;
}

.welcome-title {
  font-size: var(--forte-text-2xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-4);
}

.welcome-description {
  font-size: var(--forte-text-base);
  color: white;
  line-height: 1.6;
  margin-bottom: var(--forte-space-8);
}

.welcome-suggestions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-3);
}

.suggestions-title {
  font-size: var(--forte-text-sm);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin-bottom: var(--forte-space-2);
  text-align: left;
}

.suggestion-button {
  color: white;
  text-align: left;
  white-space: normal;
  height: auto;
  padding: var(--forte-space-4);
  border-color: var(--forte-border-light);
  transition: all var(--forte-transition-fast);
  background: var(--forte-bg-primary);
}

.suggestion-button:hover {
  border-color: var(--forte-primary);
  color: var(--forte-primary);
  transform: translateX(4px);
}

.suggestion-button:active {
  transform: scale(0.98);
}
</style>