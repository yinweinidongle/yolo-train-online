<template>
  <div class="dashboard">
    <!-- Statistics Cards -->
    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            title="数据集总数"
            :value="stats.dataset_count"
            :prefix="h(DatabaseOutlined)"
            :value-style="{ color: '#3f8600' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            title="模型总数"
            :value="stats.model_count"
            :prefix="h(AppstoreOutlined)"
            :value-style="{ color: '#1890ff' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            title="训练任务"
            :value="stats.task_count"
            :prefix="h(ExperimentOutlined)"
            :value-style="{ color: '#722ed1' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card class="stat-card">
          <a-statistic
            title="训练中"
            :value="stats.training_count"
            :prefix="h(SyncOutlined)"
            :value-style="{ color: '#cf1322' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- Recent Data -->
    <a-row :gutter="[16, 16]" class="recent-section">
      <a-col :xs="24" :lg="12">
        <a-card title="最近数据集" :loading="loading" class="content-card">
          <a-empty v-if="recentDatasets.length === 0" description="暂无数据集" />
          <a-list
            v-else
            item-layout="horizontal"
            :data-source="recentDatasets"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta :description="item.description">
                  <template #title>
                    <a>{{ item.name }}</a>
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: '#87d068' }">
                      <template #icon><database-outlined /></template>
                    </a-avatar>
                  </template>
                </a-list-item-meta>
                <template #extra>
                  <a-tag :color="getTaskTypeColor(item.task_type)">
                    {{ getTaskTypeText(item.task_type) }}
                  </a-tag>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="最近训练任务" :loading="loading" class="content-card">
          <a-empty v-if="recentTasks.length === 0" description="暂无训练任务" />
          <a-list
            v-else
            item-layout="horizontal"
            :data-source="recentTasks"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <a>{{ item.name }}</a>
                  </template>
                  <template #description>
                    <div>
                      <div>数据集: {{ item.dataset_name }}</div>
                      <div>进度: {{ item.progress.toFixed(1) }}%</div>
                    </div>
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: '#1890ff' }">
                      <template #icon><experiment-outlined /></template>
                    </a-avatar>
                  </template>
                </a-list-item-meta>
                <template #extra>
                  <a-tag :color="getStatusColor(item.status)">
                    {{ getStatusText(item.status) }}
                  </a-tag>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <!-- Quick Actions -->
    <a-card title="快速操作" class="actions-card">
      <a-row :gutter="[16, 16]">
        <a-col :xs="24" :sm="8">
          <a-button type="primary" size="large" block @click="goToDatasets">
            <template #icon><upload-outlined /></template>
            上传数据集
          </a-button>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-button type="primary" size="large" block @click="goToTraining">
            <template #icon><play-circle-outlined /></template>
            创建训练任务
          </a-button>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-button size="large" block @click="goToModels">
            <template #icon><download-outlined /></template>
            查看模型
          </a-button>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  DatabaseOutlined,
  AppstoreOutlined,
  ExperimentOutlined,
  SyncOutlined,
  UploadOutlined,
  PlayCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'
import { getStats, getDatasets, getTasks } from '@/api'

const router = useRouter()

const stats = ref({
  dataset_count: 0,
  model_count: 0,
  task_count: 0,
  training_count: 0
})

const loading = ref(false)
const recentDatasets = ref([])
const recentTasks = ref([])

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

const getStatusColor = (status) => {
  const colorMap = {
    pending: 'default',
    training: 'processing',
    completed: 'success',
    failed: 'error',
    stopped: 'warning'
  }
  return colorMap[status] || 'default'
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

const loadData = async () => {
  loading.value = true
  try {
    const [statsRes, datasetsRes, tasksRes] = await Promise.all([
      getStats(),
      getDatasets(),
      getTasks()
    ])
    
    stats.value = statsRes.data
    recentDatasets.value = datasetsRes.data.slice(0, 5)
    recentTasks.value = tasksRes.data.slice(0, 5)
  } finally {
    loading.value = false
  }
}

const goToDatasets = () => {
  router.push('/datasets')
}

const goToTraining = () => {
  router.push('/training')
}

const goToModels = () => {
  router.push('/models')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
  padding-bottom: 24px;
}

.stat-card {
  height: 100%;
  min-height: 120px;
}

.recent-section {
  margin-top: 16px;
}

.content-card {
  height: 100%;
  min-height: 400px;
}

.content-card :deep(.ant-card-body) {
  padding: 16px;
  min-height: 350px;
}

.actions-card {
  margin-top: 16px;
}

.actions-card :deep(.ant-card-body) {
  padding: 24px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .content-card {
    min-height: 300px;
  }
  
  .content-card :deep(.ant-card-body) {
    min-height: 250px;
  }
}
</style>
