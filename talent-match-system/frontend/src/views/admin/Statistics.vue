<template>
  <div class="statistics-page">
    <div class="page-header">
      <h1 class="page-title">统计分析</h1>
      <p class="page-description">平台运营数据统计与分析</p>
    </div>
    
    <div class="stats-overview">
      <div class="overview-card">
        <div class="overview-header">
          <h3 class="overview-title">用户增长趋势</h3>
        </div>
        <div class="chart-placeholder">
          <div class="bar-chart">
            <div class="bar-group" v-for="(item, index) in growthData" :key="index">
              <div class="bar" :style="{ height: item.value + '%' }"></div>
              <span class="bar-label">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="overview-card">
        <div class="overview-header">
          <h3 class="overview-title">数据概览</h3>
        </div>
        <div class="data-grid">
          <div class="data-item">
            <div class="data-value">{{ stats.total_users || 0 }}</div>
            <div class="data-label">累计用户</div>
          </div>
          <div class="data-item">
            <div class="data-value">{{ stats.total_resumes || 0 }}</div>
            <div class="data-label">简历数</div>
          </div>
          <div class="data-item">
            <div class="data-value">{{ stats.total_jobs || 0 }}</div>
            <div class="data-label">岗位数</div>
          </div>
          <div class="data-item">
            <div class="data-value">{{ stats.total_matches || 0 }}</div>
            <div class="data-label">匹配数</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="stats-detail">
      <div class="detail-card">
        <h3 class="detail-title">用户类型统计</h3>
        <div class="pie-chart-container">
          <div class="pie-chart">
            <div class="pie-segment seeker-segment" :style="{ '--percent': seekerPercent }"></div>
            <div class="pie-segment company-segment" :style="{ '--percent': companyPercent }"></div>
            <div class="pie-center">
              <span class="pie-total">{{ stats.total_users || 0 }}</span>
              <span class="pie-label">总用户</span>
            </div>
          </div>
          <div class="pie-legend">
            <div class="legend-item">
              <span class="legend-color seeker-color"></span>
              <span class="legend-text">求职者 {{ seekerPercent }}%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color company-color"></span>
              <span class="legend-text">企业 {{ companyPercent }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminAPI } from '../../api/admin'

const stats = ref({
  total_users: 0,
  total_resumes: 0,
  total_jobs: 0,
  total_matches: 0,
  job_seeker_count: 0,
  company_count: 0
})

const growthData = ref([
  { label: '1月', value: 30 },
  { label: '2月', value: 45 },
  { label: '3月', value: 60 },
  { label: '4月', value: 40 },
  { label: '5月', value: 75 },
  { label: '6月', value: 90 }
])

const seekerPercent = computed(() => {
  const total = stats.value.job_seeker_count + stats.value.company_count
  if (total === 0) return 50
  return Math.round((stats.value.job_seeker_count / total) * 100)
})

const companyPercent = computed(() => {
  return 100 - seekerPercent.value
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
.statistics-page {
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

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.overview-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.overview-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.overview-title {
  font-size: var(--font-size-h5);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.chart-placeholder {
  padding: var(--space-lg);
}

.bar-chart {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 200px;
  padding-top: var(--space-lg);
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  flex: 1;
}

.bar {
  width: 30px;
  background: var(--gradient-primary);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: height var(--duration-normal) var(--ease-out);
}

.bar-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  padding: var(--space-lg);
  gap: var(--space-lg);
}

.data-item {
  text-align: center;
  padding: var(--space-md);
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
}

.data-value {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.data-label {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.stats-detail {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-lg);
}

.detail-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-lg);
}

.detail-title {
  font-size: var(--font-size-h5);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-lg) 0;
}

.pie-chart-container {
  display: flex;
  align-items: center;
  gap: var(--space-xl);
}

.pie-chart {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: conic-gradient(
    var(--color-primary) calc(var(--percent, 50) * 1%),
    var(--color-success) calc(var(--percent, 50) * 1%)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pie-chart::before {
  content: '';
  position: absolute;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--color-bg-card);
}

.pie-center {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pie-total {
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.pie-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
}

.seeker-color {
  background: var(--color-primary);
}

.company-color {
  background: var(--color-success);
}

.legend-text {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
}
</style>