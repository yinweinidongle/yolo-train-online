import request from '@/utils/request'

// 统计信息
export function getStats() {
  return request({
    url: '/stats',
    method: 'get'
  })
}

// ========== 数据集相关 ==========
export function getDatasets() {
  return request({
    url: '/datasets',
    method: 'get'
  })
}

export function getDataset(id) {
  return request({
    url: `/datasets/${id}`,
    method: 'get'
  })
}

export function uploadDataset(formData, onProgress) {
  return request({
    url: '/datasets/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onProgress
  })
}

export function deleteDataset(id) {
  return request({
    url: `/datasets/${id}`,
    method: 'delete'
  })
}

// ========== 模型相关 ==========
export function getModels() {
  return request({
    url: '/models',
    method: 'get'
  })
}

export function getModel(id) {
  return request({
    url: `/models/${id}`,
    method: 'get'
  })
}

export function deleteModel(id) {
  return request({
    url: `/models/${id}`,
    method: 'delete'
  })
}

export function downloadModel(id) {
  return request({
    url: `/models/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

// ========== 训练任务相关 ==========
export function getTasks() {
  return request({
    url: '/tasks',
    method: 'get'
  })
}

export function getTask(id) {
  return request({
    url: `/tasks/${id}`,
    method: 'get'
  })
}

export function createTask(data) {
  return request({
    url: '/tasks/create',
    method: 'post',
    data
  })
}

export function stopTask(id) {
  return request({
    url: `/tasks/${id}/stop`,
    method: 'post'
  })
}

export function getTaskProgress(id) {
  return request({
    url: `/tasks/${id}/progress`,
    method: 'get'
  })
}
