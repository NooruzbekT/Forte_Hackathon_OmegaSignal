<script setup>
import { Menu, User } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/appStore'

const appStore = useAppStore()

function toggleSidebar() {
  appStore.toggleSidebar()
}
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <el-button
        :icon="Menu"
        @click="toggleSidebar"
        text
        class="menu-button"
      />
      <h1 class="app-title">AI Business Analyst</h1>
    </div>
    
    <div class="header-right">
      <el-button :icon="User" circle />
    </div>
  </header>
</template>

<style scoped>
.app-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid var(--forte-border-light);
  padding: 0 var(--forte-space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--forte-space-4);
}

.app-title {
  font-size: var(--forte-text-xl);
  font-weight: var(--forte-font-bold);
  color: var(--forte-text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--forte-space-3);
}
</style>