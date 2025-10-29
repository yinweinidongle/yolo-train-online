<template>
  <div class="training">
    <div class="toolbar">
      <a-space>
        <a-button type="primary" @click="showCreateModal">
          <template #icon><plus-outlined /></template>
          创建训练任务
        </a-button>
        <a-button @click="loadTasks">
          <template #icon><reload-outlined /></template>
          刷新
        </a-button>
      </a-space>
    </div>

    <a-table
      :columns="columns"
      :data-source="tasks"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          <a-space>
            <experiment-outlined />
            <span>{{ record.name }}</span>
          </a-space>
        </template>

        <template v-else-if="column.key === 'task_type'">
          <a-tag :color="getTaskTypeColor(record.task_type)">
            {{ getTaskTypeText(record.task_type) }}
          </a-tag>
        </template>

        <template v-else-if="column.key === 'progress'">
          <a-progress
            :percent="Number(record.progress.toFixed(1))"
            :status="getProgressStatus(record.status)"
            size="small"
          />
        </template>

        <template v-else-if="column.key === 'status'">
          <a-badge
            :status="getStatusBadge(record.status)"
            :text="getStatusText(record.status)"
          />
        </template>

        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button
              type="link"
              size="small"
              @click="viewTask(record)"
            >
              详情
            </a-button>
            <a-button
              v-if="record.status === 'training'"
              type="link"
              size="small"
              danger
              @click="handleStop(record.id)"
            >
              停止
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 创建训练任务对话框 -->
    <a-modal
      v-model:open="createModalVisible"
      title="创建训练任务"
      :confirm-loading="creating"
      @ok="handleCreate"
      width="700px"
    >
      <a-form
        ref="createFormRef"
        :model="createForm"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item
          label="任务名称"
          name="task_name"
          :rules="[{ required: true, message: '请输入任务名称' }]"
        >
          <a-input v-model:value="createForm.task_name" placeholder="请输入任务名称" />
        </a-form-item>

        <a-form-item
          label="选择数据集"
          name="dataset_id"
          :rules="[{ required: true, message: '请选择数据集' }]"
        >
          <a-select
            v-model:value="createForm.dataset_id"
            placeholder="请选择数据集"
            @change="handleDatasetChange"
          >
            <a-select-option
              v-for="dataset in availableDatasets"
              :key="dataset.id"
              :value="dataset.id"
            >
              {{ dataset.name }} ({{ getTaskTypeText(dataset.task_type) }})
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          label="任务类型"
          name="task_type"
          :rules="[{ required: true, message: '请选择任务类型' }]"
        >
          <a-select v-model:value="createForm.task_type" placeholder="请选择任务类型">
            <a-select-option value="detect">目标检测</a-select-option>
            <a-select-option value="classify">图像分类</a-select-option>
            <a-select-option value="segment">图像分割</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          label="模型规格"
          name="model_type"
          :rules="[{ required: true, message: '请选择模型规格' }]"
        >
          <a-select v-model:value="createForm.model_type" placeholder="请选择模型规格">
            <a-select-option value="yolo11n">YOLO11n (最快)</a-select-option>
            <a-select-option value="yolo11s">YOLO11s (小)</a-select-option>
            <a-select-option value="yolo11m">YOLO11m (中)</a-select-option>
            <a-select-option value="yolo11l">YOLO11l (大)</a-select-option>
            <a-select-option value="yolo11x">YOLO11x (超大)</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="训练轮数" name="epochs">
          <a-input-number
            v-model:value="createForm.epochs"
            :min="1"
            :max="1000"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="批次大小" name="batch_size">
          <a-input-number
            v-model:value="createForm.batch_size"
            :min="1"
            :max="128"
            style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="图像尺寸" name="img_size">
          <a-select v-model:value="createForm.img_size">
            <a-select-option :value="320">320</a-select-option>
            <a-select-option :value="416">416</a-select-option>
            <a-select-option :value="640">640</a-select-option>
            <a-select-option :value="1280">1280</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 任务详情对话框 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="训练任务详情"
      :footer="null"
      width="800px"
    >
      <a-descriptions bordered :column="2" v-if="currentTask">
        <a-descriptions-item label="任务名称" :span="2">
          {{ currentTask.name }}
        </a-descriptions-item>
        <a-descriptions-item label="数据集">
          {{ currentTask.dataset_name }}
        </a-descriptions-item>
        <a-descriptions-item label="任务类型">
          <a-tag :color="getTaskTypeColor(currentTask.task_type)">
            {{ getTaskTypeText(currentTask.task_type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="模型规格">
          {{ currentTask.model_type.toUpperCase() }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-badge
            :status="getStatusBadge(currentTask.status)"
            :text="getStatusText(currentTask.status)"
          />
        </a-descriptions-item>
        <a-descriptions-item label="训练进度" :span="2">
          <a-progress
            :percent="Number(currentTask.progress.toFixed(1))"
            :status="getProgressStatus(currentTask.status)"
          />
        </a-descriptions-item>
        <a-descriptions-item label="当前轮数">
          {{ currentTask.current_epoch }} / {{ currentTask.epochs }}
        </a-descriptions-item>
        <a-descriptions-item label="批次大小">
          {{ currentTask.batch_size }}
        </a-descriptions-item>
        <a-descriptions-item label="图像尺寸">
          {{ currentTask.img_size }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ currentTask.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="开始时间" :span="2">
          {{ currentTask.started_at || '未开始' }}
        </a-descriptions-item>
        <a-descriptions-item label="完成时间" :span="2">
          {{ currentTask.completed_at || '未完成' }}
        </a-descriptions-item>
      </a-descriptions>

      <a-divider />

      <div v-if="taskProgress.logs && taskProgress.logs.length > 0">
        <h4>训练日志</h4>
        <div class="log-container">
          <div v-for="(log, index) in taskProgress.logs" :key="index" class="log-item">
            {{ log }}
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ReloadOutlined,
  ExperimentOutlined
} from '@ant-design/icons-vue'
import { getTasks, getDatasets, createTask, stopTask, getTaskProgress } from '@/api'

const columns = [
  { title: '任务名称', key: 'name', dataIndex: 'name' },
  { title: '数据集', key: 'dataset_name', dataIndex: 'dataset_name' },
  { title: '任务类型', key: 'task_type', dataIndex: 'task_type' },
  { title: '模型', key: 'model_type', dataIndex: 'model_type' },
  { title: '进度', key: 'progress', dataIndex: 'progress' },
  { title: '状态', key: 'status', dataIndex: 'status' },
  { title: '创建时间', key: 'created_at', dataIndex: 'created_at' },
  { title: '操作', key: 'action', width: 150 }
]

const tasks = ref([])
const loading = ref(false)
const pagination = reactive({
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`
})

const createModalVisible = ref(false)
const creating = ref(false)
const createFormRef = ref()
const createForm = reactive({
  task_name: '',
  dataset_id: null,
  task_type: 'detect',
  model_type: 'yolo11n',
  epochs: 100,
  batch_size: 16,
  img_size: 640
})
const availableDatasets = ref([])

const detailModalVisible = ref(false)
const currentTask = ref(null)
const taskProgress = ref({})

let refreshTimer = null

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
    pending: 'default',
    training: 'processing',
    completed: 'success',
    failed: 'error',
    stopped: 'warning'
  }
  return badgeMap[status] || 'default'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待中',
    training: '训练中',
    completed: '已完成',
    failed: '失败',
    stopped: '已停止'
  }
  return textMap[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'training') return 'active'
  return 'normal'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks()
    tasks.value = res.data
  } finally {
    loading.value = false
  }
}

const showCreateModal = async () => {
  createModalVisible.value = true
  
  // 加载可用数据集
  try {
    const res = await getDatasets()
    availableDatasets.value = res.data.filter(d => d.status === 'ready')
  } catch (error) {
    console.error('加载数据集失败:', error)
  }
}

const handleDatasetChange = (datasetId) => {
  const dataset = availableDatasets.value.find(d => d.id === datasetId)
  if (dataset) {
    createForm.task_type = dataset.task_type
  }
}

const handleCreate = async () => {
  try {
    await createFormRef.value.validate()
    
    creating.value = true
    await createTask(createForm)
    
    message.success('训练任务创建成功')
    createModalVisible.value = false
    loadTasks()
  } catch (error) {
    console.error('创建失败:', error)
  } finally {
    creating.value = false
  }
}

const viewTask = async (record) => {
  currentTask.value = record
  detailModalVisible.value = true
  
  // 获取训练进度
  try {
    const res = await getTaskProgress(record.id)
    taskProgress.value = res.data.progress
  } catch (error) {
    console.error('获取进度失败:', error)
  }
}

const handleStop = async (id) => {
  try {
    await stopTask(id)
    message.success('任务已停止')
    loadTasks()
  } catch (error) {
    console.error('停止失败:', error)
  }
}

onMounted(() => {
  loadTasks()
  
  // 每10秒刷新一次任务列表
  refreshTimer = setInterval(() => {
    loadTasks()
  }, 10000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.training {
  width: 100%;
}

.toolbar {
  margin-bottom: 16px;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
}

.log-item {
  font-family: monospace;
  font-size: 12px;
  line-height: 1.8;
  color: #333;
}
</style>
