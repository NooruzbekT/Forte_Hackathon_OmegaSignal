<script setup>
import { PictureFilled } from '@element-plus/icons-vue'
</script>

<template>
  <div class="chart-empty">
    <el-icon :size="80" color="var(--forte-text-disabled)">
      <PictureFilled />
    </el-icon>
    <p class="empty-text">Нет диаграмм для отображения</p>
  </div>
</template>

<style scoped>
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--forte-space-12);
  background: var(--forte-bg-secondary);
  border-radius: var(--forte-radius-md);
  min-height: 300px;
}

.empty-text {
  margin-top: var(--forte-space-4);
  font-size: var(--forte-text-base);
  color: var(--forte-text-secondary);
}
</style>