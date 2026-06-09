<template>
  <div class="admin-login-container">
    <div class="admin-login-background">
      <div class="bg-grid"></div>
    </div>
    
    <div class="admin-login-card">
      <div class="admin-login-header">
        <div class="admin-logo-container">
          <div class="admin-logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          <h1 class="admin-logo-title">平台管理后台</h1>
        </div>
        <p class="admin-logo-subtitle">人才智能匹配系统 - 管理员登录</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" class="admin-login-form" @submit.prevent="handleSubmit">
        <el-form-item prop="username">
          <div class="input-wrapper">
            <el-icon class="input-icon"><User /></el-icon>
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名"
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'" 
              placeholder="请输入密码"
              class="custom-input"
            />
            <el-icon 
              class="toggle-password" 
              @click="showPassword = !showPassword"
            >
              <View v-if="!showPassword" />
              <Hide v-else />
            </el-icon>
          </div>
        </el-form-item>
        
        <el-form-item prop="captcha">
          <div class="input-wrapper captcha-input-wrapper">
            <el-icon class="input-icon"><Key /></el-icon>
            <el-input 
              v-model="form.captcha" 
              placeholder="请输入验证码"
              maxlength="4"
              class="custom-input"
            />
            <div class="captcha-img" @click="refreshCaptcha">
              <img :src="captchaUrl" alt="验证码" />
            </div>
          </div>
        </el-form-item>
        
        <el-form-item class="submit-item">
          <button 
            type="submit" 
            :class="['submit-btn', { loading: loading }]"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span>登录</span>
          </button>
        </el-form-item>
      </el-form>
      
      <div class="admin-login-footer">
        <span>© 2024 人才智能匹配系统 - 管理员后台</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide, Key } from '@element-plus/icons-vue'
import { userAPI } from '../api/index'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const showPassword = ref(false)
const captchaKey = ref(Math.random())

const captchaUrl = computed(() => {
  return `/api/user/captcha?key=${captchaKey.value}`
})

const form = reactive({
  username: '',
  password: '',
  captcha: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为4位', trigger: 'blur' }
  ]
}

const refreshCaptcha = () => {
  captchaKey.value = Math.random()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const userData = await userAPI.adminLogin({
          username: form.username,
          password: form.password,
          captcha: form.captcha
        })
        
        localStorage.setItem('user', JSON.stringify(userData))
        localStorage.setItem('role', 'admin')
        localStorage.setItem('userId', userData.id)
        
        ElMessage.success('登录成功')
        router.push('/admin/dashboard')
      } catch (error) {
        refreshCaptcha()
        ElMessage.error('登录失败：' + (error.response?.data?.detail || error.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
.admin-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.admin-login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.admin-login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: rgba(30, 41, 59, 0.95);
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.admin-login-header {
  text-align: center;
  margin-bottom: 32px;
}

.admin-logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.admin-logo-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.admin-logo-icon svg {
  width: 28px;
  height: 28px;
}

.admin-logo-title {
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.admin-logo-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.admin-login-form {
  margin-bottom: 24px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0 16px;
  height: 48px;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
  background: rgba(15, 23, 42, 0.9);
}

.input-icon {
  color: #64748b;
  font-size: 18px;
  margin-right: 12px;
  flex-shrink: 0;
}

.custom-input {
  flex: 1;
  min-width: 0;
}

.toggle-password {
  color: #64748b;
  cursor: pointer;
  font-size: 18px;
  margin-left: 12px;
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.toggle-password:hover {
  color: #3b82f6;
}

.captcha-input-wrapper {
  padding-right: 8px;
}

.captcha-img {
  flex-shrink: 0;
  width: 80px;
  height: 32px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.1);
}

.captcha-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.submit-item {
  margin-top: 24px;
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.admin-login-footer {
  text-align: center;
  font-size: 12px;
  color: #64748b;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

@media (max-width: 576px) {
  .admin-login-card {
    padding: 24px;
  }
  
  .admin-logo-icon {
    width: 40px;
    height: 40px;
  }
  
  .admin-logo-icon svg {
    width: 24px;
    height: 24px;
  }
  
  .admin-logo-title {
    font-size: 20px;
  }
}
</style>

<style>
.admin-login-container .el-input__wrapper,
.admin-login-container .el-form-item .el-input__wrapper {
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  background: none !important;
  background-color: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  inset: auto !important;
}

.admin-login-container .el-input .el-input__wrapper::before,
.admin-login-container .el-input .el-input__wrapper::after {
  display: none !important;
}

.admin-login-container .el-input__inner,
.admin-login-container .el-form-item .el-input__inner {
  height: auto !important;
  line-height: inherit !important;
  padding: 0 !important;
  margin: 0 !important;
  font-size: 14px !important;
  background: none !important;
  background-color: transparent !important;
  color: #f1f5f9 !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  outline: none !important;
}

.admin-login-container .el-input__inner::placeholder {
  color: #64748b !important;
  opacity: 1 !important;
}

.admin-login-container .el-form-item__error {
  padding-left: 0 !important;
  margin-top: 4px !important;
  position: relative !important;
  top: auto !important;
  left: auto !important;
  color: #ef4444 !important;
}
</style>