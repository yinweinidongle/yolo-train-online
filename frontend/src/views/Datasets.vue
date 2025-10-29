<template>
  <div class="datasets">
    <div class="toolbar">
      <a-space>
        <a-button type="primary" @click="showUploadModal">
          <template #icon><upload-outlined /></template>
          上传数据集
        </a-button>
        <a-button @click="loadDatasets">
          <template #icon><reload-outlined /></template>
          刷新
        </a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data-source="datasets"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a-space>
            <database-outlined />
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

        <template v-else-if="column.key === 'status'">
          <a-badge
            :status="getStatusBadge(record.status)"
            :text="getStatusText(record.status)"
          />
        </template>

        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="viewDataset(record)">
              详情
            </a-button>
            <a-popconfirm
              title="确定要删除此数据集吗？"
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

    <!-- 上传数据集对话框 -->
    <a-modal
      v-model:open="uploadModalVisible"
      title="上传数据集"
      :confirm-loading="uploading"
      @ok="handleUpload"
      width="600px"
    >
      <a-form
        ref="uploadFormRef"
        :model="uploadForm"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item
          label="数据集名称"
          name="name"
          :rules="[{ required: true, message: '请输入数据集名称' }]"
        >
          <a-input v-model:value="uploadForm.name" placeholder="请输入数据集名称" />
        </a-form-item>

        <a-form-item
          label="任务类型"
          name="task_type"
          :rules="[{ required: true, message: '请选择任务类型' }]"
        >
          <a-select v-model:value="uploadForm.task_type" placeholder="请选择任务类型">
            <a-select-option value="detect">目标检测</a-select-option>
            <a-select-option value="classify">图像分类</a-select-option>
            <a-select-option value="segment">图像分割</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="描述" name="description">
          <a-textarea
            v-model:value="uploadForm.description"
            placeholder="请输入数据集描述"
            :rows="3"
          />
        </a-form-item>

        <a-form-item
          label="数据集文件"
          name="file"
          :rules="[{ required: true, message: '请选择数据集文件' }]"
        >
          <a-upload
            v-model:file-list="fileList"
            :before-upload="beforeUpload"
            :max-count="1"
            accept=".zip"
          >
            <a-button>
              <upload-outlined />
              选择ZIP文件
            </a-button>
          </a-upload>
          <div style="margin-top: 8px; color: #999; font-size: 12px">
            数据集格式说明：<br />
            • 检测/分割：需包含 train/images, train/labels, val/images, val/labels 目录<br />
            • 分类：需包含 train/, val/ 目录，每个类别一个子文件夹
          </div>
        </a-form-item>

        <a-form-item
          v-if="uploadProgress > 0"
          label="上传进度"
          :wrapper-col="{ span: 18 }"
        >
          <a-progress :percent="uploadProgress" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 数据集详情对话框 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="数据集详情"
      :footer="null"
      width="600px"
    >
      <a-descriptions bordered :column="2" v-if="currentDataset">
        <a-descriptions-item label="名称" :span="2">
          {{ currentDataset.name }}
        </a-descriptions-item>
        <a-descriptions-item label="任务类型">
          <a-tag :color="getTaskTypeColor(currentDataset.task_type)">
            {{ getTaskTypeText(currentDataset.task_type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-badge
            :status="getStatusBadge(currentDataset.status)"
            :text="getStatusText(currentDataset.status)"
          />
        </a-descriptions-item>
        <a-descriptions-item label="文件数量">
          {{ currentDataset.file_count }}
        </a-descriptions-item>
        <a-descriptions-item label="大小">
          {{ formatSize(currentDataset.size) }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间" :span="2">
          {{ currentDataset.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">
          {{ currentDataset.description || '无' }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  UploadOutlined,
  ReloadOutlined,
  DatabaseOutlined
} from '@ant-design/icons-vue'
import { getDatasets, uploadDataset, deleteDataset } from '@/api'

const columns = [
  { title: '数据集名称', key: 'name', dataIndex: 'name' },
  { title: '任务类型', key: 'task_type', dataIndex: 'task_type' },
  { title: '文件数量', key: 'file_count', dataIndex: 'file_count' },
  { title: '大小', key: 'size', dataIndex: 'size' },
  { title: '状态', key: 'status', dataIndex: 'status' },
  { title: '创建时间', key: 'created_at', dataIndex: 'created_at' },
  { title: '操作', key: 'action', width: 150 }
]

const datasets = ref([])
const loading = ref(false)
const pagination = reactive({
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const uploadModalVisible = ref(false)
const uploading = ref(false)
const uploadFormRef = ref()
const uploadForm = reactive({
  name: '',
  task_type: '',
  description: '',
  file: null
})
const fileList = ref([])
const uploadProgress = ref(0)

const detailModalVisible = ref(false)
const currentDataset = ref(null)

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

const getStatusBadge = (status) => {
  const badgeMap = {
    processing: 'processing',
    ready: 'success',
    error: 'error'
  }
  return badgeMap[status] || 'default'
}

const getStatusText = (status) => {
  const textMap = {
    processing: '处理中',
    ready: '就绪',
    error: '错误'
  }
  return textMap[status] || status
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const loadDatasets = async () => {
  loading.value = true
  try {
    const res = await getDatasets()
    datasets.value = res.data
  } finally {
    loading.value = false
  }
}

const showUploadModal = () => {
  uploadModalVisible.value = true
  uploadForm.name = ''
  uploadForm.task_type = ''
  uploadForm.description = ''
  fileList.value = []
  uploadProgress.value = 0
}

const beforeUpload = (file) => {
  uploadForm.file = file
  return false
}

const handleUpload = async () => {
  try {
    await uploadFormRef.value.validate()
    
    if (!uploadForm.file) {
      message.error('请选择文件')
      return
    }

    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('name', uploadForm.name)
    formData.append('task_type', uploadForm.task_type)
    formData.append('description', uploadForm.description)

    uploading.value = true
    uploadProgress.value = 0

    await uploadDataset(formData, (progressEvent) => {
      uploadProgress.value = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
    })

    message.success('数据集上传成功')
    uploadModalVisible.value = false
    loadDatasets()
  } catch (error) {
    console.error('上传失败:', error)
  } finally {
    uploading.value = false
  }
}

const viewDataset = (record) => {
  currentDataset.value = record
  detailModalVisible.value = true
}

const handleDelete = async (id) => {
  try {
    await deleteDataset(id)
    message.success('删除成功')
    loadDatasets()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  loadDatasets()
})
</script>

<style scoped>
.datasets {
  width: 100%;
}

.toolbar {
  margin-bottom: 16px;
}
</style>
