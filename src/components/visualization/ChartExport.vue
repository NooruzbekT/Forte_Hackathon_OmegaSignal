<script setup>
import { Download } from '@element-plus/icons-vue'
import { exportMermaidAsPNG, exportMermaidAsSVG } from '@/utils/generators/mermaidExporter'
import { saveAs } from 'file-saver'
import { useNotification } from '@/composables/useNotification'

const props = defineProps({
  chartId: {
    type: String,
    required: true
  },
  filename: {
    type: String,
    default: 'chart'
  }
})

const { success, error } = useNotification()

async function handleExport(format) {
  try {
    let blob
    
    if (format === 'png') {
      blob = await exportMermaidAsPNG(props.chartId)
      saveAs(blob, `${props.filename}.png`)
    } else if (format === 'svg') {
      blob = exportMermaidAsSVG(props.chartId)
      saveAs(blob, `${props.filename}.svg`)
    }
    
    success(`Диаграмма экспортирована как ${format.toUpperCase()}`)
  } catch (err) {
    error('Ошибка при экспорте диаграммы')
    console.error(err)
  }
}
</script>

<template>
  <div class="chart-export">
    <el-dropdown trigger="click">
      <el-button :icon="Download" size="small">
        Экспорт
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="handleExport('png')">
            PNG
          </el-dropdown-item>
          <el-dropdown-item @click="handleExport('svg')">
            SVG
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<style scoped>
.chart-export {
  display: inline-flex;
}
</style>