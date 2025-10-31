<template>
  <div class="inference">
    <a-row :gutter="16">
      <!-- 左侧：上传和配置区 -->
      <a-col :span="10">
        <a-card title="模型验证" :bordered="false">
          <a-form layout="vertical">
            <a-form-item label="选择模型">
              <a-select
                v-model:value="selectedModelId"
                placeholder="请选择模型"
                :loading="modelsLoading"
                @change="handleModelChange"
              >
                <a-select-option v-for="model in models" :key="model.id" :value="model.id">
                  {{ model.name }} ({{ model.model_type }})
                </a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="上传图片">
              <a-upload
                v-model:file-list="fileList"
                list-type="picture-card"
                accept="image/*"
                :before-upload="beforeUpload"
                :max-count="1"
                @remove="handleRemove"
                @preview="handlePreview"
              >
                <div v-if="fileList.length < 1">
                  <plus-outlined />
                  <div style="margin-top: 8px">上传图片</div>
                </div>
              </a-upload>
            </a-form-item>

            <a-form-item label="置信度阈值">
              <a-slider
                v-model:value="confidence"
                :min="0.1"
                :max="1"
                :step="0.05"
                :marks="{ 0.1: '0.1', 0.5: '0.5', 1: '1.0' }"
              />
              <span>{{ confidence }}</span>
            </a-form-item>

            <a-form-item label="IoU阈值">
              <a-slider
                v-model:value="iou"
                :min="0.1"
                :max="1"
                :step="0.05"
                :marks="{ 0.1: '0.1', 0.5: '0.5', 1: '1.0' }"
              />
              <span>{{ iou }}</span>
            </a-form-item>

            <a-form-item>
              <a-button
                type="primary"
                block
                size="large"
                :loading="inferencing"
                :disabled="!selectedModelId || fileList.length === 0"
                @click="handleInference"
              >
                <template #icon><thunderbolt-outlined /></template>
                开始识别
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <!-- 右侧：结果展示区 -->
      <a-col :span="14">
        <a-card title="识别结果" :bordered="false">
          <div v-if="!inferenceResult" class="empty-state">
            <a-empty description="请选择模型并上传图片进行识别" />
          </div>

          <div v-else>
            <!-- 结果图片 -->
            <div class="result-image">
              <img :src="inferenceResult.image" alt="识别结果" />
            </div>

            <!-- 统计信息 -->
            <a-row :gutter="16" class="stats">
              <a-col :span="8">
                <a-statistic
                  title="检测对象数"
                  :value="inferenceResult.detections.length"
                  :value-style="{ color: '#3f8600', fontSize: '20px' }"
                >
                  <template #prefix>
                    <aim-outlined />
                  </template>
                </a-statistic>
              </a-col>
              <a-col :span="8">
                <a-statistic
                  title="推理时间"
                  :value="inferenceResult.inference_time"
                  suffix="ms"
                  :value-style="{ color: '#1890ff', fontSize: '20px' }"
                >
                  <template #prefix>
                    <clock-circle-outlined />
                  </template>
                </a-statistic>
              </a-col>
              <a-col :span="8">
                <a-statistic
                  title="平均置信度"
                  :value="averageConfidence"
                  suffix="%"
                  :precision="1"
                  :value-style="{ color: '#cf1322', fontSize: '20px' }"
                >
                  <template #prefix>
                    <check-circle-outlined />
                  </template>
                </a-statistic>
              </a-col>
            </a-row>

            <!-- 检测详情 -->
            <div class="detections">
              <h4>检测详情</h4>
              <a-table
                :columns="detectionColumns"
                :data-source="inferenceResult.detections"
                :pagination="false"
                size="small"
                :scroll="{ y: 150 }"
              >
                <template #bodyCell="{ column, record, index }">
                  <template v-if="column.key === 'index'">
                    {{ index + 1 }}
                  </template>
                  <template v-else-if="column.key === 'class'">
                    <a-tag :color="getClassColor(record.class)">
                      {{ record.class }}
                    </a-tag>
                  </template>
                  <template v-else-if="column.key === 'confidence'">
                    <a-progress
                      :percent="(record.confidence * 100)"
                      :show-info="true"
                      :format="(percent) => percent.toFixed(1) + '%'"
                      :stroke-color="{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }"
                    />
                  </template>
                  <template v-else-if="column.key === 'bbox'">
                    {{ formatBbox(record.bbox) }}
                  </template>
                </template>
              </a-table>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 图片预览 -->
    <a-modal
      :open="previewVisible"
      :footer="null"
      @cancel="previewVisible = false"
    >
      <img :src="previewImage" style="width: 100%" alt="预览" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ThunderboltOutlined,
  AimOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons-vue'
import { getModels, runInference } from '@/api'

const detectionColumns = [
  { title: '序号', key: 'index', width: 60 },
  { title: '类别', key: 'class', dataIndex: 'class' },
  { title: '置信度', key: 'confidence', dataIndex: 'confidence' },
  { title: '边界框', key: 'bbox', dataIndex: 'bbox' }
]

const models = ref([])
const modelsLoading = ref(false)
const selectedModelId = ref(null)
const fileList = ref([])
const confidence = ref(0.25)
const iou = ref(0.45)
const inferencing = ref(false)
const inferenceResult = ref(null)
const previewVisible = ref(false)
const previewImage = ref('')

const colorList = ['blue', 'green', 'orange', 'red', 'purple', 'cyan', 'magenta']

const averageConfidence = computed(() => {
  if (!inferenceResult.value || inferenceResult.value.detections.length === 0) {
    return 0
  }
  const sum = inferenceResult.value.detections.reduce((acc, det) => acc + det.confidence, 0)
  return (sum / inferenceResult.value.detections.length) * 100
})

const loadModels = async () => {
  modelsLoading.value = true
  try {
    const res = await getModels()
    models.value = res.data
  } finally {
    modelsLoading.value = false
  }
}

const handleModelChange = () => {
  inferenceResult.value = null
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件!')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('图片大小不能超过10MB!')
    return false
  }
  
  // 清空之前的结果
  inferenceResult.value = null
  
  return false // 阻止自动上传
}

const handleRemove = () => {
  inferenceResult.value = null
}

const handlePreview = async (file) => {
  if (!file.url && !file.preview) {
    file.preview = await getBase64(file.originFileObj)
  }
  previewImage.value = file.url || file.preview
  previewVisible.value = true
}

const getBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = (error) => reject(error)
  })
}

const handleInference = async () => {
  if (!selectedModelId.value) {
    message.warning('请先选择模型')
    return
  }
  if (fileList.value.length === 0) {
    message.warning('请先上传图片')
    return
  }

  inferencing.value = true
  try {
    const formData = new FormData()
    formData.append('image', fileList.value[0].originFileObj)
    formData.append('model_id', selectedModelId.value)
    formData.append('confidence', confidence.value)
    formData.append('iou', iou.value)

    const res = await runInference(formData)
    inferenceResult.value = res.data
    message.success('识别完成!')
  } catch (error) {
    console.error('识别失败:', error)
  } finally {
    inferencing.value = false
  }
}

const getClassColor = (className) => {
  const hash = className.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colorList[hash % colorList.length]
}

const formatBbox = (bbox) => {
  if (!bbox || bbox.length !== 4) return '-'
  return `[${bbox.map(v => Math.round(v)).join(', ')}]`
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.inference {
  width: 100%;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.result-image {
  text-align: center;
  margin-bottom: 12px;
}

.result-image img {
  max-width: 100%;
  max-height: 600px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats {
  margin: 12px 0;
}

.detections {
  margin-top: 12px;
}

.detections h4 {
  margin-bottom: 8px;
  font-size: 14px;
}
</style>
