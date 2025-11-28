<script setup>
import { computed } from 'vue'
import { formatPercent } from '@/utils/formatters/numberFormatter'

const props = defineProps({
  quality: {
    type: Number,
    required: true
  }
})

const badgeType = computed(() => {
  if (props.quality >= 0.9) return 'success'
  if (props.quality >= 0.7) return 'warning'
  return 'danger'
})

const qualityText = computed(() => formatPercent(props.quality))
</script>

<template>
  <el-tag :type="badgeType" size="small">
    Качество: {{ qualityText }}
  </el-tag>
</template>