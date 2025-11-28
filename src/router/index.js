import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'

const routes = [
  {
    path: '/',
    name: 'main',
    component: MainView
  },
  {
    path: '/documents',
    name: 'documents',
    component: () => import('@/views/DocumentsView.vue')
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/HistoryView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router