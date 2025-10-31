import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: 'datasets',
        name: 'Datasets',
        component: () => import('@/views/Datasets.vue'),
        meta: { title: '数据集管理', requiresAuth: true }
      },
      {
        path: 'training',
        name: 'Training',
        component: () => import('@/views/Training.vue'),
        meta: { title: '模型训练', requiresAuth: true }
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/Models.vue'),
        meta: { title: '模型管理', requiresAuth: true }
      },
      {
        path: 'inference',
        name: 'Inference',
        component: () => import('@/views/Inference.vue'),
        meta: { title: '模型验证', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'
  
  // 如果路由需要认证且用户未登录
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } 
  // 如果已登录且访问登录页，跳转到首页
  else if (to.path === '/login' && isLoggedIn) {
    next('/dashboard')
  } 
  else {
    next()
  }
})

export default router
