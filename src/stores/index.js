import { createPinia } from 'pinia'

export const pinia = createPinia()

export { useChatStore } from './chatStore'
export { useDocumentStore } from './documentStore'
export { useLayerStore } from './layerStore'
export { useAppStore } from './appStore'