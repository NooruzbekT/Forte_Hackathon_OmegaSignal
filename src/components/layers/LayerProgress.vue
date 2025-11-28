<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentLayer: {
    type: Number,
    default: null,
    validator: (value) => value === null || (value >= 1 && value <= 5)
  }
})

const layers = [
  {
    id: 1,
    name: 'Intent Understanding',
    icon: 'BrainIcon',
    description: 'Анализ намерения пользователя'
  },
  {
    id: 2,
    name: 'Requirement Gathering',
    icon: 'DocumentCheckIcon',
    description: 'Сбор требований через диалог'
  },
  {
    id: 3,
    name: 'RAG Search',
    icon: 'SearchIcon',
    description: 'Поиск похожих документов'
  },
  {
    id: 4,
    name: 'Document Generation',
    icon: 'DocumentIcon',
    description: 'Генерация документа'
  },
  {
    id: 5,
    name: 'Quality Validation',
    icon: 'CheckCircleIcon',
    description: 'Проверка качества'
  }
]

function getLayerStatus(layerId) {
  if (props.currentLayer === null) return 'pending'
  if (layerId < props.currentLayer) return 'completed'
  if (layerId === props.currentLayer) return 'active'
  return 'pending'
}

const progressPercentage = computed(() => {
  if (props.currentLayer === null) return 0
  return (props.currentLayer / 5) * 100
})
</script>

<template>
  <div class="layer-progress">
    <!-- Progress Bar -->
    <div class="progress-bar-container">
      <div 
        class="progress-bar-fill"
        :style="{ width: `${progressPercentage}%` }"
      />
    </div>

    <!-- Layer Steps -->
    <div class="layer-steps">
      <div
        v-for="layer in layers"
        :key="layer.id"
        :class="[
          'layer-step',
          `layer-step-${getLayerStatus(layer.id)}`
        ]"
      >
        <!-- Circle -->
        <div class="layer-circle">
          <el-icon v-if="getLayerStatus(layer.id) === 'completed'">
            <Check />
          </el-icon>
          <el-icon v-else-if="getLayerStatus(layer.id) === 'active'" class="spin">
            <Loading />
          </el-icon>
          <span v-else>{{ layer.id }}</span>
        </div>

        <!-- Info -->
        <div class="layer-info">
          <span class="layer-name">{{ layer.name }}</span>
          <span class="layer-description">{{ layer.description }}</span>
        </div>

        <!-- Connector Line -->
        <div 
          v-if="layer.id < 5"
          class="layer-connector"
          :class="{ 'connector-active': layer.id < currentLayer }"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layer-progress {
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
  padding: var(--forte-space-6);
}

.progress-bar-container {
  width: 100%;
  height: 4px;
  background: var(--forte-border-light);
  border-radius: var(--forte-radius-full);
  margin-bottom: var(--forte-space-6);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--forte-gradient);
  transition: width 0.5s ease;
  border-radius: var(--forte-radius-full);
}

.layer-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.layer-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  text-align: center;
}

.layer-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--forte-font-bold);
  font-size: var(--forte-text-base);
  transition: all var(--forte-transition-base);
  position: relative;
  z-index: 2;
  background: var(--forte-bg-primary);
  border: 3px solid var(--forte-border-light);
  color: white;
}

.layer-step-active .layer-circle {
  background: var(--forte-bg-primary);
  color: white;
  box-shadow: 0 0 0 4px var(--forte-primary-lighter);
}

.layer-step-completed .layer-circle {
  background: var(--forte-bg-primary);
  color: white;
}

.layer-info {
  margin-top: var(--forte-space-3);
  display: flex;
  flex-direction: column;
  gap: var(--forte-space-1);
}

.layer-name {
  font-weight: var(--forte-font-semibold);
  font-size: var(--forte-text-sm);
  color: var(--forte-text-primary);
}

.layer-description {
  font-size: var(--forte-text-xs);
  color: var(--forte-text-secondary);
}

.layer-connector {
  position: absolute;
  top: 24px;
  left: calc(50% + 24px);
  right: calc(-50% + 24px);
  height: 3px;
  background: var(--forte-border-light);
  transition: background-color 0.5s ease;
  z-index: 1;
}

.connector-active {
  background: var(--forte-primary);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .layer-steps {
    flex-wrap: wrap;
    gap: var(--forte-space-6);
  }
  
  .layer-step {
    flex-basis: calc(50% - var(--forte-space-3));
  }
  
  .layer-connector {
    display: none;
  }
}

@media (max-width: 640px) {
  .layer-description {
    display: none;
  }
  
  .layer-circle {
    width: 40px;
    height: 40px;
  }
}
</style>