<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Подтверждение'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Подтвердить'
  },
  cancelText: {
    type: String,
    default: 'Отмена'
  },
  type: {
    type: String,
    default: 'warning'
  }
})

const emit = defineEmits(['confirm', 'cancel'])
const visible = ref(false)

function show() {
  visible.value = true
}

function hide() {
  visible.value = false
}

function handleConfirm() {
  emit('confirm')
  hide()
}

function handleCancel() {
  emit('cancel')
  hide()
}

defineExpose({ show, hide })
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="400px"
  >
    <p class="dialog-message">{{ message }}</p>
    
    <template #footer>
      <el-button @click="handleCancel">
        {{ cancelText }}
      </el-button>
      <el-button
        :type="type"
        @click="handleConfirm"
      >
        {{ confirmText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-message {
  font-size: var(--forte-text-base);
  color: var(--forte-text-primary);
  line-height: 1.6;
}
</style>