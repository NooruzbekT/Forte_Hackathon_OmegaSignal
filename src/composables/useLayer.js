import { computed } from 'vue'
import { useLayerStore } from '@/stores/layerStore'
import { LAYER_NAMES } from '@/utils/helpers/constants'

export function useLayer() {
  const layerStore = useLayerStore()

  const currentLayer = computed(() => layerStore.currentLayer)
  const currentLayerName = computed(() => 
    currentLayer.value ? LAYER_NAMES[currentLayer.value] : null
  )
  const progress = computed(() => layerStore.progress)
  const completedLayers = computed(() => layerStore.completedLayers)

  function setLayer(layerId) {
    layerStore.setCurrentLayer(layerId)
  }

  function completeCurrentLayer() {
    if (currentLayer.value) {
      layerStore.completeLayer(currentLayer.value)
    }
  }

  function updateLayerData(data) {
    if (currentLayer.value) {
      layerStore.updateLayerData(currentLayer.value, data)
    }
  }

  function reset() {
    layerStore.reset()
  }

  return {
    currentLayer,
    currentLayerName,
    progress,
    completedLayers,
    setLayer,
    completeCurrentLayer,
    updateLayerData,
    reset
  }
}