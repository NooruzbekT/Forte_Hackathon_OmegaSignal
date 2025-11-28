// main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import ElementPlus from 'element-plus'
import ru from 'element-plus/es/locale/lang/ru'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import 'element-plus/dist/index.css'
import './assets/styles/main.css'

import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

async function checkAPIHealth() {
  try {
    const response = await apiClient.get(API_ENDPOINTS.HEALTH)
    console.log('✅ API Health:', response)
  } catch (error) {
    console.warn('⚠️ API not available:', error.message)
    console.warn('Using MOCK mode')
  }
}

app.use(pinia)
app.use(ElementPlus, { locale: ru })

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
