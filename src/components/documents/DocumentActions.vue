<script setup>
import { Download, Delete, Edit, Share } from '@element-plus/icons-vue'

const emit = defineEmits(['download', 'delete', 'edit', 'share'])
</script>

<template>
  <div class="document-actions">
    <el-button
      :icon="Download"
      @click="emit('download')"
      size="small"
    >
      Скачать
    </el-button>
    
    <el-button
      :icon="Edit"
      @click="emit('edit')"
      size="small"
    >
      Редактировать
    </el-button>
    
    <el-button
      :icon="Share"
      @click="emit('share')"
      size="small"
    >
      Поделиться
    </el-button>
    
    <el-button
      :icon="Delete"
      @click="emit('delete')"
      type="danger"
      size="small"
    >
      Удалить
    </el-button>
  </div>
</template>

<style scoped>
.document-actions {
  display: flex;
  gap: var(--forte-space-2);
  flex-wrap: wrap;
}
</style>