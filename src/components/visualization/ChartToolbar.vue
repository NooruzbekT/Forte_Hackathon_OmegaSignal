<script setup>
import { ZoomIn, ZoomOut, Refresh, FullScreen } from '@element-plus/icons-vue'

const emit = defineEmits(['zoom-in', 'zoom-out', 'refresh', 'fullscreen'])
</script>

<template>
  <div class="chart-toolbar">
    <el-button-group>
      <el-button
        :icon="ZoomIn"
        size="small"
        @click="emit('zoom-in')"
      />
      <el-button
        :icon="ZoomOut"
        size="small"
        @click="emit('zoom-out')"
      />
      <el-button
        :icon="Refresh"
        size="small"
        @click="emit('refresh')"
      />
      <el-button
        :icon="FullScreen"
        size="small"
        @click="emit('fullscreen')"
      />
    </el-button-group>
  </div>
</template>

<style scoped>
.chart-toolbar {
  display: flex;
  gap: var(--forte-space-2);
}
</style>