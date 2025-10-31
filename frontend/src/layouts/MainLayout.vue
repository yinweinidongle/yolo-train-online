<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible>
      <div class="logo">
        <img src="/logo.svg" alt="YOLO" v-if="!collapsed" />
        <span v-if="!collapsed">图像识别可视化训练平台</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="dashboard">
          <dashboard-outlined />
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="datasets">
          <database-outlined />
          <span>数据集管理</span>
        </a-menu-item>
        <a-menu-item key="training">
          <experiment-outlined />
          <span>模型训练</span>
        </a-menu-item>
        <a-menu-item key="models">
          <appstore-outlined />
          <span>模型管理</span>
        </a-menu-item>
        <a-menu-item key="inference">
          <scan-outlined />
          <span>模型验证</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background: #fff; padding: 0 24px">
        <div class="header-content">
          <h2>{{ currentTitle }}</h2>
          <a-space>
            <a-badge :count="trainingCount" :offset="[-5, 5]">
              <a-button type="text" @click="refreshData">
                <template #icon><sync-outlined :spin="loading" /></template>
                刷新
              </a-button>
            </a-badge>
            <a-dropdown>
              <a-button type="text">
                <template #icon><user-outlined /></template>
                {{ username }}
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="logout" @click="handleLogout">
                    <logout-outlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </a-layout-header>
      <a-layout-content style="margin: 16px">
        <div style="padding: 24px; background: #fff; min-height: 360px">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" :key="$route.path" />
            </keep-alive>
          </router-view>
        </div>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        图像识别可视化训练平台 ©2024 
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  AppstoreOutlined,
  SyncOutlined,
  ScanOutlined,
  UserOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'
import { getStats } from '@/api'
import { message } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const selectedKeys = ref(['dashboard'])
const loading = ref(false)
const trainingCount = ref(0)
const username = ref(localStorage.getItem('username') || 'admin')

const currentTitle = computed(() => {
  return route.meta.title || '仪表盘'
})

const handleMenuClick = ({ key }) => {
  router.push(`/${key}`)
}

const refreshData = async () => {
  loading.value = true
  try {
    const res = await getStats()
    trainingCount.value = res.data.training_count
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('isLoggedIn')
  localStorage.removeItem('username')
  message.success('退出成功')
  router.push('/login')
}

onMounted(() => {
  selectedKeys.value = [route.name.toLowerCase()]
  refreshData()
  // 每30秒刷新一次训练状态
  setInterval(refreshData, 30000)
})
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  gap: 8px;
}

.logo img {
  width: 32px;
  height: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
}
</style>
