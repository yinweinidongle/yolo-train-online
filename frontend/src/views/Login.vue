<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/logo.svg" alt="Logo" class="logo" />
        <h1>图像识别可视化训练平台</h1>
        <p>Image Recognition Visual Training Platform</p>
      </div>
      
      <a-form
        :model="formState"
        name="login"
        autocomplete="off"
        @finish="handleLogin"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input
            v-model:value="formState.username"
            size="large"
            placeholder="用户名"
          >
            <template #prefix>
              <user-outlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password
            v-model:value="formState.password"
            size="large"
            placeholder="密码"
          >
            <template #prefix>
              <lock-outlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const loading = ref(false)

const formState = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  loading.value = true
  
  try {
    // 模拟登录验证
    await new Promise(resolve => setTimeout(resolve, 500))
    
    if (formState.username === 'admin' && formState.password === '123456') {
      // 保存登录状态
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', formState.username)
      
      message.success('登录成功')
      
      // 跳转到首页
      router.push('/dashboard')
    } else {
      message.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header .logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #333;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-tips {
  margin-top: 24px;
}

@media (max-width: 768px) {
  .login-box {
    padding: 24px;
  }
  
  .login-header h1 {
    font-size: 20px;
  }
}
</style>
