<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <h1 class="logo-title">人才智能匹配系统</h1>
        </div>
        <p class="logo-subtitle">AI驱动的人才与职位精准匹配平台</p>
      </div>
      
      <div class="role-selector">
        <div class="role-tabs">
          <button 
            :class="['role-tab', { active: form.role === 'job_seeker' }]" 
            @click="form.role = 'job_seeker'"
          >
            <div class="role-icon seeker-icon">👤</div>
            <span>求职者</span>
          </button>
          <button 
            :class="['role-tab', { active: form.role === 'company' }]" 
            @click="form.role = 'company'"
          >
            <div class="role-icon company-icon">🏢</div>
            <span>企业</span>
          </button>
        </div>
      </div>
      
      <div class="login-tabs">
        <button 
          :class="['tab-btn', { active: !isRegister }]" 
          @click="isRegister = false"
        >
          登录
        </button>
        <button 
          :class="['tab-btn', { active: isRegister }]" 
          @click="isRegister = true"
        >
          注册
        </button>
        <div class="tab-indicator" :style="{ transform: `translateX(${isRegister ? '100%' : '0'})` }"></div>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" class="login-form" @submit.prevent="handleSubmit">
        <el-form-item prop="phone">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Phone /></el-icon>
            <el-input 
              v-model="form.phone" 
              placeholder="请输入手机号"
              maxlength="11"
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item v-if="isRegister" prop="nickname">
          <div class="input-wrapper">
            <el-icon class="input-icon"><User /></el-icon>
            <el-input 
              v-model="form.nickname" 
              placeholder="请输入昵称"
              maxlength="20"
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item v-if="isRegister" prop="code">
          <div class="input-wrapper code-input-wrapper">
            <el-icon class="input-icon"><ChatDotRound /></el-icon>
            <el-input 
              v-model="form.code" 
              placeholder="请输入验证码"
              maxlength="6"
              class="custom-input"
            />
            <el-button 
              :class="['code-btn', { disabled: codeDisabled }]"
              @click="sendCode"
              :disabled="codeDisabled"
            >
              {{ codeButtonText }}
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item prop="password">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input 
              v-model="form.password" 
              :type="showPassword ? 'text' : 'password'" 
              :placeholder="isRegister ? '设置密码（至少6位）' : '请输入密码'"
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
        
        <el-form-item v-if="isRegister" prop="confirmPassword">
          <div class="input-wrapper">
            <el-icon class="input-icon"><Lock /></el-icon>
            <el-input 
              v-model="form.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码"
              class="custom-input"
            />
          </div>
        </el-form-item>
        
        <el-form-item class="submit-item">
          <button 
            type="submit" 
            :class="['submit-btn', { loading: loading }]"
            :disabled="loading"
          >
            <span v-if="loading" class="loading-spinner"></span>
            <span>{{ isRegister ? '注册' : '登录' }}</span>
          </button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>{{ isRegister ? '已有账号？' : '还没有账号？' }}</span>
        <a @click="toggleMode">{{ isRegister ? '立即登录' : '立即注册' }}</a>
      </div>
      
      <div v-if="sentCode" class="code-tip">
        <el-icon><CircleCheckFilled /></el-icon>
        <span>测试验证码：{{ sentCode }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, ChatDotRound, Lock, View, Hide, CircleCheckFilled, User } from '@element-plus/icons-vue'
import { authService } from '../services/auth'
import { userAPI } from '../api/index'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const isRegister = ref(false)
const codeDisabled = ref(false)
const codeButtonText = ref('获取验证码')
const sentCode = ref('')
const showPassword = ref(false)

const form = reactive({
  phone: '',
  nickname: '',
  code: '',
  password: '',
  confirmPassword: '',
  role: 'job_seeker'
})

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1\d{10}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  phone: [
    { required: true, validator: validatePhone, trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在2-20个字符之间', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const sendCode = async () => {
  if (!form.phone || !/^1\d{10}$/.test(form.phone)) {
    ElMessage.error('请输入正确的手机号')
    return
  }
  
  try {
    const response = await userAPI.sendCode({ phone: form.phone })
    sentCode.value = response.code
    ElMessage.success('验证码已发送')
    
    codeDisabled.value = true
    let count = 60
    codeButtonText.value = `${count}s`
    
    const timer = setInterval(() => {
      count--
      if (count <= 0) {
        clearInterval(timer)
        codeDisabled.value = false
        codeButtonText.value = '获取验证码'
      } else {
        codeButtonText.value = `${count}s`
      }
    }, 1000)
  } catch (error) {
    ElMessage.error('发送验证码失败：' + (error.response?.data?.detail || '未知错误'))
  }
}

const toggleMode = () => {
  isRegister.value = !isRegister.value
  sentCode.value = ''
  form.code = ''
  form.confirmPassword = ''
  form.nickname = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isRegister.value) {
          await userAPI.register({
            phone: form.phone,
            nickname: form.nickname,
            code: form.code,
            password: form.password,
            role: form.role
          })
          ElMessage.success('注册成功，请登录')
          isRegister.value = false
          form.code = ''
          form.confirmPassword = ''
        } else {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          localStorage.removeItem('role')
          localStorage.removeItem('roles')
          localStorage.removeItem('userId')
          
          const userData = await authService.login({
            phone: form.phone,
            password: form.password,
            role: form.role
          })
          ElMessage.success('登录成功')
          
          localStorage.setItem('role', form.role)
          
          if (form.role === 'job_seeker') {
            router.push('/job-seeker/home')
          } else if (form.role === 'company') {
            router.push('/company/home')
          } else {
            router.push('/job-seeker/home')
          }
        }
      } catch (error) {
        ElMessage.error((isRegister.value ? '注册' : '登录') + '失败：' + (error.response?.data?.detail || error.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-ai);
  position: relative;
  overflow: hidden;
  padding: var(--space-lg);
}

.login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  animation: float 20s infinite ease-in-out;
}

.bg-circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.bg-circle-2 {
  width: 300px;
  height: 300px;
  bottom: -80px;
  left: -80px;
  animation-delay: -5s;
}

.bg-circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 60%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -30px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(15px, 15px) scale(1.02); }
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: var(--color-bg-card);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-modal);
  padding: var(--space-2xl);
  animation: slideUp 0.6s var(--ease-out);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.logo-icon {
  width: 48px;
  height: 48px;
  background: var(--gradient-ai);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.logo-icon svg {
  width: 28px;
  height: 28px;
}

.logo-title {
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.logo-subtitle {
  font-size: var(--font-size-caption);
  color: var(--color-text-tertiary);
  margin: 0;
}

.role-selector {
  margin-bottom: var(--space-lg);
}

.role-tabs {
  display: flex;
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.role-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border: none;
  background: transparent;
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--duration-short) var(--ease-out);
}

.role-tab:hover {
  background: rgba(var(--color-primary-rgb), 0.1);
}

.role-tab.active {
  background: var(--color-primary);
  color: white;
}

.role-icon {
  font-size: 18px;
}

.login-tabs {
  display: flex;
  position: relative;
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
  padding: 4px;
  margin-bottom: var(--space-xl);
}

.tab-btn {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  border: none;
  background: transparent;
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: color var(--duration-short) var(--ease-out);
  position: relative;
  z-index: 1;
}

.tab-btn.active {
  color: var(--color-primary);
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transition: transform var(--duration-normal) var(--ease-in-out);
}

.login-form {
  margin-bottom: var(--space-lg);
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: 0 var(--space-md);
  height: 48px;
  width: 100%;
  box-sizing: border-box;
}

.input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-input-focus);
  background: var(--color-bg-card);
}

.input-icon {
  color: var(--color-text-tertiary);
  font-size: 18px;
  margin-right: var(--space-sm);
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.custom-input {
  flex: 1;
  min-width: 0;
}

.toggle-password {
  color: var(--color-text-tertiary);
  cursor: pointer;
  font-size: 18px;
  margin-left: var(--space-sm);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  transition: color var(--duration-short) var(--ease-out);
}

.toggle-password:hover {
  color: var(--color-primary);
}

.toggle-password:hover {
  color: var(--color-primary);
}

.code-input-wrapper {
  padding-right: var(--space-sm);
}

.code-btn {
  flex-shrink: 0;
  padding: var(--space-xs) var(--space-md);
  font-size: var(--font-size-caption);
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-bg);
  color: var(--color-primary);
  border: none;
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
}

.code-btn:hover:not(.disabled) {
  background: var(--color-primary);
  color: white;
}

.code-btn.disabled {
  background: var(--color-bg-page);
  color: var(--color-text-tertiary);
  cursor: not-allowed;
}

.submit-item {
  margin-top: var(--space-lg);
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: var(--radius-lg);
  background: var(--gradient-primary);
  color: white;
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
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

.login-footer {
  text-align: center;
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.login-footer a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  margin-left: var(--space-xs);
}

.login-footer a:hover {
  text-decoration: underline;
}

.code-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  margin-top: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-success-bg);
  border-radius: var(--radius-md);
  color: var(--color-success);
  font-size: var(--font-size-caption);
}

@media (max-width: 576px) {
  .login-card {
    padding: var(--space-xl);
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
  }
  
  .logo-icon svg {
    width: 24px;
    height: 24px;
  }
  
  .logo-title {
    font-size: var(--font-size-h4);
  }
}
</style>

<style>
/* Complete reset of Element Plus input styles within login form */
.login-container .el-input__wrapper,
.login-container .el-form-item .el-input__wrapper {
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

.login-container .el-input .el-input__wrapper::before,
.login-container .el-input .el-input__wrapper::after {
  display: none !important;
}

.login-container .el-input__inner,
.login-container .el-form-item .el-input__inner {
  height: auto !important;
  line-height: inherit !important;
  padding: 0 !important;
  margin: 0 !important;
  font-size: var(--font-size-body) !important;
  background: none !important;
  background-color: transparent !important;
  color: var(--color-text-primary) !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  outline: none !important;
}

.login-container .el-input__inner::placeholder {
  color: var(--color-text-tertiary) !important;
  opacity: 1 !important;
}

.login-container .el-form-item__error {
  padding-left: 0 !important;
  margin-top: 4px !important;
  position: relative !important;
  top: auto !important;
  left: auto !important;
}
</style>
