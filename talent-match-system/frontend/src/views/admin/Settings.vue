<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">系统设置</h1>
      <p class="page-description">配置平台系统参数</p>
    </div>
    
    <div class="settings-container">
      <div class="settings-section">
        <h3 class="section-title">系统信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行状态</span>
            <span class="info-value status-active">正常运行</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库</span>
            <span class="info-value">达梦数据库</span>
          </div>
          <div class="info-item">
            <span class="info-label">服务端口</span>
            <span class="info-value">8000</span>
          </div>
        </div>
      </div>
      
      <div class="settings-section">
        <h3 class="section-title">安全设置</h3>
        <div class="setting-item">
          <div class="setting-header">
            <span class="setting-label">密码复杂度要求</span>
            <span class="setting-desc">设置用户密码的最小长度要求</span>
          </div>
          <div class="setting-control">
            <el-input 
              type="number" 
              v-model="passwordMinLength"
              min="6"
              max="32"
              class="setting-input"
            />
            <span class="setting-unit">位</span>
          </div>
        </div>
        
        <div class="setting-item">
          <div class="setting-header">
            <span class="setting-label">登录失败限制</span>
            <span class="setting-desc">连续登录失败多少次后锁定账号</span>
          </div>
          <div class="setting-control">
            <el-input 
              type="number" 
              v-model="maxLoginAttempts"
              min="3"
              max="10"
              class="setting-input"
            />
            <span class="setting-unit">次</span>
          </div>
        </div>
      </div>
      
      <div class="settings-section">
        <h3 class="section-title">数据管理</h3>
        <div class="action-buttons">
          <el-button type="primary" @click="backupData">
            <el-icon><Download /></el-icon>
            备份数据
          </el-button>
          <el-button @click="clearCache">
            <el-icon><Refresh /></el-icon>
            清除缓存
          </el-button>
        </div>
      </div>
      
      <div class="settings-section">
        <h3 class="section-title">操作日志</h3>
        <div class="log-container">
          <div class="log-item" v-for="(log, index) in logs" :key="index">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-action">{{ log.action }}</span>
            <span class="log-user">{{ log.user }}</span>
          </div>
        </div>
      </div>
      
      <div class="save-section">
        <el-button type="primary" size="large" @click="saveSettings">
          <el-icon><Check /></el-icon>
          保存设置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Download, Refresh, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const passwordMinLength = ref(8)
const maxLoginAttempts = ref(5)

const logs = ref([
  { time: '2024-01-15 10:30:25', action: '用户登录', user: '138****8888' },
  { time: '2024-01-15 10:25:18', action: '用户管理', user: '138****8888' },
  { time: '2024-01-15 10:20:45', action: '查看统计', user: '138****8888' },
  { time: '2024-01-15 10:15:32', action: '系统设置', user: '138****8888' }
])

const backupData = () => {
  ElMessage.info('数据备份功能开发中')
}

const clearCache = () => {
  ElMessage.info('缓存清除功能开发中')
}

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}
</script>

<style scoped>
.settings-page {
  padding: var(--space-lg);
}

.page-header {
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-xs) 0;
}

.page-description {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin: 0;
}

.settings-container {
  max-width: 800px;
}

.settings-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.section-title {
  font-size: var(--font-size-h5);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-lg) 0;
  padding-bottom: var(--space-md);
  border-bottom: 1px solid var(--color-border-light);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-md);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
}

.info-label {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
}

.info-value {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.status-active {
  color: var(--color-success);
}

.setting-item {
  margin-bottom: var(--space-lg);
}

.setting-item:last-child {
  margin-bottom: 0;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.setting-label {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.setting-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.setting-control {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.setting-input {
  width: 120px;
}

.setting-unit {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
}

.action-buttons {
  display: flex;
  gap: var(--space-md);
}

.log-container {
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: var(--space-lg);
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-family: var(--font-mono);
}

.log-action {
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
  flex: 1;
}

.log-user {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.save-section {
  display: flex;
  justify-content: flex-end;
}
</style>