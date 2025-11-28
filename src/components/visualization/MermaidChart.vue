<script setup>
import { ref, watch, onMounted } from 'vue'
import VueMermaidString from 'vue-mermaid-string'

const props = defineProps({
  diagram: {
    type: String,
    required: true
  },
  config: {
    type: Object,
    default: () => ({
      theme: 'default',
      fontSize: 14
    })
  }
})

const chartId = ref(`mermaid-${Date.now()}`)
const hasError = ref(false)
const errorMessage = ref('')

function validateDiagram() {
  if (!props.diagram || !props.diagram.trim()) {
    hasError.value = true
    errorMessage.value = 'Пустая диаграмма'
    return false
  }
  hasError.value = false
  return true
}

watch(() => props.diagram, () => {
  validateDiagram()
})

onMounted(() => {
  validateDiagram()
})
</script>

<template>
  <div :id="chartId" class="mermaid-chart">
    <div v-if="hasError" class="chart-error">
      <el-alert
        type="error"
        :title="errorMessage"
        :closable="false"
      />
    </div>
    
    <VueMermaidString
      v-else
      :value="diagram"
      :options="config"
    />
  </div>
</template>

<style scoped>
.mermaid-chart {
  width: 100%;
  min-height: 200px;
  padding: var(--forte-space-4);
  background: white;
  border-radius: var(--forte-radius-md);
  border: 1px solid var(--forte-border-light);
}

.chart-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}
</style>