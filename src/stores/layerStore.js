import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLayerStore = defineStore('layer', () => {
  // State
  const currentLayer = ref(null)
  const layerHistory = ref([])
  const layerData = ref({
    1: { status: 'pending', data: null }, // Intent Understanding
    2: { status: 'pending', data: null }, // Requirement Gathering
    3: { status: 'pending', data: null }, // RAG Search
    4: { status: 'pending', data: null }, // Document Generation
    5: { status: 'pending', data: null }  // Quality Validation
  })

  // Getters
  const currentLayerStatus = computed(() => {
    return currentLayer.value ? layerData.value[currentLayer.value].status : null
  })
  
  const completedLayers = computed(() => {
    return Object.entries(layerData.value)
      .filter(([_, layer]) => layer.status === 'completed')
      .map(([id]) => parseInt(id))
  })

  const progress = computed(() => {
    return (completedLayers.value.length / 5) * 100
  })

  // Actions
  function setCurrentLayer(layer) {
    if (layer >= 1 && layer <= 5) {
      currentLayer.value = layer
      updateLayerStatus(layer, 'active')
      
      layerHistory.value.push({
        layer,
        timestamp: new Date().toISOString()
      })
    }
  }

  function updateLayerStatus(layer, status) {
    if (layerData.value[layer]) {
      layerData.value[layer].status = status
    }
  }

  function updateLayerData(layer, data) {
    if (layerData.value[layer]) {
      layerData.value[layer].data = data
    }
  }

  function completeLayer(layer) {
    updateLayerStatus(layer, 'completed')
    
    // Automatically move to next layer
    if (layer < 5) {
      setCurrentLayer(layer + 1)
    }
  }

  function reset() {
    currentLayer.value = null
    layerHistory.value = []
    Object.keys(layerData.value).forEach(key => {
      layerData.value[key] = { status: 'pending', data: null }
    })
  }

  return {
    currentLayer,
    layerHistory,
    layerData,
    currentLayerStatus,
    completedLayers,
    progress,
    setCurrentLayer,
    updateLayerStatus,
    updateLayerData,
    completeLayer,
    reset
  }
})