<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h1 class="page-title">数据概览</h1>
      <p class="page-description">实时监控平台运营数据</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon users-icon">
          <el-icon :size="32"><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon resume-icon">
          <el-icon :size="32"><Files /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_resumes || 0 }}</div>
          <div class="stat-label">简历数量</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon job-icon">
          <el-icon :size="32"><Briefcase /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_jobs || 0 }}</div>
          <div class="stat-label">岗位数量</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon match-icon">
          <el-icon :size="32"><Link /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_matches || 0 }}</div>
          <div class="stat-label">匹配次数</div>
        </div>
      </div>
    </div>
    
    <div class="charts-grid">
      <div class="chart-card">
        <h3 class="chart-title">用户类型分布</h3>
        <div class="user-distribution">
          <div class="distribution-item">
            <div class="distribution-bar-seeker"></div>
            <span class="distribution-label">求职者: {{ stats.job_seeker_count || 0 }}</span>
          </div>
          <div class="distribution-item">
            <div class="distribution-bar-company"></div>
            <span class="distribution-label">企业: {{ stats.company_count || 0 }}</span>
          </div>
        </div>
      </div>
      
      <div class="chart-card">
        <h3 class="chart-title">平台数据统计</h3>
        <div class="stats-summary">
          <div class="summary-item">
            <span class="summary-value">{{ stats.job_seeker_count || 0 }}</span>
            <span class="summary-label">求职者</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-item">
            <span class="summary-value">{{ stats.company_count || 0 }}</span>
            <span class="summary-label">企业</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-item">
            <span class="summary-value">{{ stats.total_jobs || 0 }}</span>
            <span class="summary-label">岗位</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, Files, Briefcase, Link } from '@element-plus/icons-vue'
import { adminAPI } from '../../api/admin'

const stats = ref({
  total_users: 0,
  total_resumes: 0,
  total_jobs: 0,
  total_matches: 0,
  job_seeker_count: 0,
  company_count: 0
})

const loadStats = async () => {
  try {
    const data = await adminAPI.getStats()
    if (data) {
      stats.value = data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.admin-dashboard {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  box-shadow: var(--shadow-card);
  transition: transform var(--duration-normal) var(--ease-out);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.users-icon {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.resume-icon {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.job-icon {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.match-icon {
  background: var(--color-info-bg);
  color: var(--color-info);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.chart-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  box-shadow: var(--shadow-card);
}

.chart-title {
  font-size: var(--font-size-h5);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-lg) 0;
}

.user-distribution {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.distribution-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.distribution-bar-seeker {
  height: 8px;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
  width: 70%;
}

.distribution-bar-company {
  height: 8px;
  background: var(--gradient-success);
  border-radius: var(--radius-full);
  width: 30%;
}

.distribution-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-summary {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
}

.summary-value {
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.summary-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.summary-divider {
  width: 1px;
  height: 40px;
  background: var(--color-border-light);
}
</style>