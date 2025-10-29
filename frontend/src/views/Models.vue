<template>
  <div class="models">
    <div class="toolbar">
      <a-space>
        <a-button @click="loadModels">
          <template #icon><reload-outlined /></template>
          刷新
        </a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data-source="models"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a-space>
            <appstore-outlined />
            <span>{{ record.name }}</span>
          </a-space>
        </template>

        <template v-else-if="column.key === 'task_type'">
          <a-tag :color="getTaskTypeColor(record.task_type)">
            {{ getTaskTypeText(record.task_type) }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'size'">
          {{ formatSize(record.size) }}
        </template>

        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="viewModel(record)">
              详情
            </a-button>
            <a-button type="link" size="small" @click="handleDownload(record.id)">
              下载
            </a-button>
            <a-popconfirm
              title="确定要删除此模型吗？"
              ok-text="确定"
              cancel-text="取消"
              @confirm="handleDelete(record.id)"
            >
              <a-button type="link" size="small" danger>
                删除
              </a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 模型详情对话框 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="模型详情"
      :footer="null"
      width="700px"
    >
      <a-descriptions bordered :column="2" v-if="currentModel">
        <a-descriptions-item label="模型名称" :span="2">
          {{ currentModel.name }}
        </a-descriptions-item>
        <a-descriptions-item label="任务类型">
          <a-tag :color="getTaskTypeColor(currentModel.task_type)">
            {{ getTaskTypeText(currentModel.task_type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="模型规格">
          {{ currentModel.model_type.toUpperCase() }}
        </a-descriptions-item>
        <a-descriptions-item label="文件大小">
          {{ formatSize(currentModel.size) }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ currentModel.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="权重路径" :span="2">
          <a-typography-text copyable>{{ currentModel.weight_path }}</a-typography-text>
        </a-descriptions-item>
      </a-descriptions>

      <a-divider />

      <div v-if="currentModel.metrics && Object.keys(currentModel.metrics).length > 0">
        <h4>训练参数</h4>
        <a-descriptions bordered :column="2">
          <a-descriptions-item
            v-for="(value, key) in currentModel.metrics"
            :key="key"
            :label="formatMetricLabel(key)"
          >
            {{ value }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  AppstoreOutlined
} from '@ant-design/icons-vue'
import { getModels, deleteModel, downloadModel } from '@/api'

const columns = [
  { title: '模型名称', key: 'name', dataIndex: 'name' },
  { title: '任务类型', key: 'task_type', dataIndex: 'task_type' },
  { title: '模型规格', key: 'model_type', dataIndex: 'model_type' },
  { title: '文件大小', key: 'size', dataIndex: 'size' },
  { title: '创建时间', key: 'created_at', dataIndex: 'created_at' },
  { title: '操作', key: 'action', width: 200 }
]

const models = ref([])
const loading = ref(false)
const pagination = reactive({
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const detailModalVisible = ref(false)
const currentModel = ref(null)

const getTaskTypeColor = (type) => {
  const colorMap = {
    detect: 'blue',
    classify: 'green',
    segment: 'purple'
  }
  return colorMap[type] || 'default'
}

const getTaskTypeText = (type) => {
  const textMap = {
    detect: '目标检测',
    classify: '图像分类',
    segment: '图像分割'
  }
  return textMap[type] || type
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatMetricLabel = (key) => {
  const labelMap = {
    epochs: '训练轮数',
    batch_size: '批次大小',
    img_size: '图像尺寸',
    precision: '精确率',
    recall: '召回率',
    mAP50: 'mAP@0.5',
    'mAP50-95': 'mAP@0.5:0.95'
  }
  return labelMap[key] || key
}

const loadModels = async () => {
  loading.value = true
  try {
    const res = await getModels()
    models.value = res.data
  } finally {
    loading.value = false
  }
}

const viewModel = (record) => {
  currentModel.value = record
  detailModalVisible.value = true
}

const handleDownload = async (id) => {
  try {
    const res = await downloadModel(id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `model_${id}.pt`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    message.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
  }
}

const handleDelete = async (id) => {
  try {
    await deleteModel(id)
    message.success('删除成功')
    loadModels()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.models {
  width: 100%;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
