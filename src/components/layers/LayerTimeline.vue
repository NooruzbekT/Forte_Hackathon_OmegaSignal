<script setup>
import { computed } from 'vue'
import { Check } from '@element-plus/icons-vue'

const props = defineProps({
  layers: {
    type: Array,
    required: true
  },
  currentLayer: {
    type: Number,
    default: null
  }
})

function getLayerStatus(layerId) {
  if (!props.currentLayer) return 'pending'
  if (layerId < props.currentLayer) return 'completed'
  if (layerId === props.currentLayer) return 'active'
  return 'pending'
}
</script>

<template>
  <div class="layer-timeline">
    <div
      v-for="(layer, index) in layers"
      :key="layer.id"
      :class="['timeline-item', `timeline-item-${getLayerStatus(layer.id)}`]"
    >
      <div class="timeline-marker">
        <el-icon v-if="getLayerStatus(layer.id) === 'completed'">
          <Check />
        </el-icon>
        <span v-else>{{ layer.id }}</span>
      </div>
      
      <div class="timeline-content">
        <h4 class="timeline-title">{{ layer.name }}</h4>
        <p class="timeline-description">{{ layer.description }}</p>
      </div>
      
      <div 
        v-if="index < layers.length - 1"
        :class="[
          'timeline-connector',
          { 'timeline-connector-active': getLayerStatus(layer.id) === 'completed' }
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.layer-timeline {
  position: relative;
  padding: var(--forte-space-4);
}

.timeline-item {
  position: relative;
  display: flex;
  gap: var(--forte-space-4);
  padding-bottom: var(--forte-space-6);
}

.timeline-marker {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--forte-bg-secondary);
  border: 3px solid var(--forte-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-secondary);
  flex-shrink: 0;
  position: relative;
  z-index: 2;
  transition: all var(--forte-transition-base);
}

.timeline-item-active .timeline-marker {
  background: var(--forte-primary);
  border-color: var(--forte-primary);
  color: white;
  box-shadow: 0 0 0 4px var(--forte-primary-lighter);
}

.timeline-item-completed .timeline-marker {
  background: var(--forte-success);
  border-color: var(--forte-success);
  color: white;
}

.timeline-content {
  flex: 1;
  padding-top: var(--forte-space-2);
}

.timeline-title {
  font-size: var(--forte-text-base);
  font-weight: var(--forte-font-semibold);
  color: var(--forte-text-primary);
  margin: 0 0 var(--forte-space-1);
}

.timeline-description {
  font-size: var(--forte-text-sm);
  color: var(--forte-text-secondary);
  margin: 0;
}

.timeline-connector {
  position: absolute;
  left: 19px;
  top: 40px;
  width: 3px;
  height: calc(100% - 40px);
  background: var(--forte-border-light);
  transition: background-color var(--forte-transition-base);
}

.timeline-connector-active {
  background: var(--forte-primary);
}
</style>