<template>
  <div class="home-page">
    <div class="welcome-section">
      <h2 class="welcome-title">
        <span class="wave-emoji">👋</span>
        欢迎回来
      </h2>
      <p class="welcome-subtitle">{{ welcomeMessage }}</p>
    </div>
    
    <div class="stats-grid">
      <div v-for="stat in statsData" :key="stat.title" class="stat-card">
        <div class="stat-header">
          <div class="stat-icon" :style="{ background: stat.gradient }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div v-if="stat.trend" :class="['stat-trend', stat.trendType]">
            <el-icon><Top v-if="stat.trendType === 'up'" /><Bottom v-else /></el-icon>
            <span>{{ stat.trend }}</span>
          </div>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-title">{{ stat.title }}</div>
        <div class="stat-desc">{{ stat.desc }}</div>
      </div>
    </div>
    
    <div class="content-grid">
      <div class="chart-section">
        <div class="section-header">
          <h3 class="section-title">匹配趋势</h3>
          <div class="section-actions">
            <button 
              :class="['time-btn', { active: timeRange === '7d' }]"
              @click="timeRange = '7d'"
            >近7天</button>
            <button 
              :class="['time-btn', { active: timeRange === '30d' }]"
              @click="timeRange = '30d'"
            >近30天</button>
          </div>
        </div>
        <div ref="trendChartRef" class="trend-chart"></div>
      </div>
      
      <div class="quick-actions">
        <div class="section-header">
          <h3 class="section-title">快捷操作</h3>
        </div>
        <div class="actions-list">
          <router-link 
            v-for="action in quickActions" 
            :key="action.path"
            :to="action.path"
            class="action-item"
          >
            <div class="action-icon" :style="{ background: action.color }">
              <el-icon :size="20"><component :is="action.icon" /></el-icon>
            </div>
            <span class="action-text">{{ action.label }}</span>
            <el-icon class="action-arrow"><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="recent-matches-section">
      <div class="section-header">
        <h3 class="section-title">最近匹配记录</h3>
        <router-link :to="userRole === 'job_seeker' ? '/delivery' : '/match-result'" class="view-all">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </router-link>
      </div>
      <div class="matches-table">
        <div class="table-header">
          <div class="col col-resume">简历</div>
          <div class="col col-job">岗位</div>
          <div class="col col-score">匹配分数</div>
          <div class="col col-tags">匹配点</div>
          <div class="col col-time">时间</div>
        </div>
        <div v-if="recentMatches.length === 0" class="empty-matches">
          <el-icon :size="48" color="#C7C7CC"><Document /></el-icon>
          <p>暂无匹配记录</p>
          <router-link to="/job-list" class="empty-action">去浏览岗位</router-link>
        </div>
        <div 
          v-for="(match, index) in recentMatches" 
          :key="index"
          class="table-row"
        >
          <div class="col col-resume">{{ match.resume_name || '简历 ' + match.resume_id }}</div>
          <div class="col col-job">{{ match.job_name || '岗位 ' + match.job_id }}</div>
          <div class="col col-score">
            <span :class="['score-badge', getScoreClass(match.match_score)]">
              {{ match.match_score }}分
            </span>
          </div>
          <div class="col col-tags">
            <span class="match-tag" v-if="match.match_tags">{{ match.match_tags }}</span>
            <span class="no-tag" v-else>-</span>
          </div>
          <div class="col col-time">{{ formatTime(match.create_time) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Document, Upload, Star, ChatDotRound, OfficeBuilding,
  Search, User, TrendCharts, ArrowRight, Top, Bottom
} from '@element-plus/icons-vue'
import { resumeAPI, jobAPI, matchAPI } from '../api'

const router = useRouter()
const trendChartRef = ref(null)
const timeRange = ref('7d')
const userRole = ref('')
let chartInstance = null

const resumeCount = ref(0)
const favoriteCount = ref(0)
const deliveryCount = ref(0)
const jobCount = ref(0)
const matchedResumesCount = ref(0)
const recentMatches = ref([])

const welcomeMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好，开启元气满满的一天！'
  if (hour < 18) return '下午好，继续努力工作吧！'
  return '晚上好，辛苦了一天了！'
})

const statsData = computed(() => {
  if (userRole.value === 'job_seeker') {
    return [
      {
        title: '我的简历',
        value: resumeCount.value,
        desc: '已上传简历数量',
        icon: Document,
        gradient: 'var(--gradient-primary)',
        trend: null
      },
      {
        title: '我的收藏',
        value: favoriteCount.value,
        desc: '已收藏岗位',
        icon: Star,
        gradient: 'linear-gradient(135deg, #FF6B6B, #FFB400)',
        trend: null
      },
      {
        title: '我的投递',
        value: deliveryCount.value,
        desc: '已投递简历',
        icon: ChatDotRound,
        gradient: 'linear-gradient(135deg, #8B5CF6, #1A73E8)',
        trend: null
      }
    ]
  }
  
  return [
    {
      title: '我的岗位',
      value: jobCount.value,
      desc: '已发布岗位',
      icon: OfficeBuilding,
      gradient: 'var(--gradient-primary)',
      trend: null
    },
    {
      title: '匹配人才',
      value: matchedResumesCount.value,
      desc: '匹配成功人才数',
      icon: User,
      gradient: 'var(--gradient-match)',
      trend: null
    },
    {
      title: '收到简历',
      value: 0,
      desc: '收到投递数量',
      icon: ChatDotRound,
      gradient: 'linear-gradient(135deg, #8B5CF6, #1A73E8)',
      trend: null
    }
  ]
})

const quickActions = computed(() => {
  if (userRole.value === 'job_seeker') {
    return [
      { label: '上传简历', path: '/ai-parse-test', icon: Upload, color: 'var(--gradient-primary)' },
      { label: '浏览岗位', path: '/job-list', icon: Search, color: 'var(--gradient-match)' },
      { label: '我的收藏', path: '/favorite', icon: Star, color: 'linear-gradient(135deg, #FF6B6B, #FFB400)' }
    ]
  }
  
  return [
    { label: '发布岗位', path: '/job-management', icon: OfficeBuilding, color: 'var(--gradient-primary)' },
    { label: '匹配结果', path: '/match-result', icon: Search, color: 'var(--gradient-match)' },
    { label: '岗位AI分析', path: '/ai-job-parse', icon: TrendCharts, color: 'linear-gradient(135deg, #8B5CF6, #1A73E8)' }
  ]
})

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const getStats = async () => {
  try {
    const storedRole = localStorage.getItem('role')
    const userStr = localStorage.getItem('user')
    
    if (storedRole) {
      userRole.value = storedRole
    } else if (userStr) {
      try {
        const user = JSON.parse(userStr)
        userRole.value = user.role || 'job_seeker'
      } catch (e) {
        userRole.value = 'job_seeker'
      }
    } else {
      userRole.value = 'job_seeker'
    }
    
    if (userRole.value === 'job_seeker') {
      try {
        const resumes = await resumeAPI.getResumes()
        resumeCount.value = resumes.length
      } catch (error) {
        resumeCount.value = 0
      }
      
      try {
        const favorites = await favoriteAPI.getFavorites()
        favoriteCount.value = favorites.length
      } catch (error) {
        favoriteCount.value = 0
      }
      
      try {
        const deliveries = await deliveryAPI.getDeliveries()
        deliveryCount.value = deliveries.length
      } catch (error) {
        deliveryCount.value = 0
      }
    } else {
      try {
        const jobs = await jobAPI.getJobs()
        jobCount.value = jobs.length
      } catch (error) {
        jobCount.value = 0
      }
      
      try {
        const matches = await matchAPI.getMatchRecords()
        const uniqueResumes = new Set(matches.map(m => m.resume_id))
        matchedResumesCount.value = uniqueResumes.size
      } catch (error) {
        matchedResumesCount.value = 0
      }
    }
    
    try {
      const matches = await matchAPI.getMatchRecords()
      recentMatches.value = matches.slice(0, 5).map(match => ({
        ...match,
        resume_name: '简历 ' + match.resume_id,
        job_name: '岗位 ' + match.job_id
      }))
    } catch (error) {
      recentMatches.value = []
    }
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(trendChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E8E8E8',
      borderWidth: 1,
      textStyle: { color: '#1D1D1F' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timeRange.value === '7d' 
        ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        : Array.from({ length: 30 }, (_, i) => `${i + 1}日`),
      axisLine: { lineStyle: { color: '#E8E8E8' } },
      axisLabel: { color: '#8E8E93' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F5F5F7', type: 'dashed' } },
      axisLabel: { color: '#8E8E93' }
    },
    series: [{
      name: '匹配次数',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#1A73E8' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(26, 115, 232, 0.2)' },
            { offset: 1, color: 'rgba(26, 115, 232, 0.02)' }
          ]
        }
      },
      data: timeRange.value === '7d'
        ? [3, 5, 2, 8, 6, 4, 7]
        : Array.from({ length: 30 }, () => Math.floor(Math.random() * 10) + 1)
    }]
  }
  
  chartInstance.setOption(option)
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(timeRange, () => {
  nextTick(() => {
    initTrendChart()
  })
})

onMounted(async () => {
  await nextTick()
  getStats()
  nextTick(() => {
    initTrendChart()
    window.addEventListener('resize', handleResize)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.home-page {
  padding: var(--space-lg) 0;
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.welcome-section {
  margin-bottom: var(--space-xl);
}

.welcome-title {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.wave-emoji {
  font-size: 32px;
  animation: wave 1.5s ease-in-out infinite;
  display: inline-block;
}

@keyframes wave {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(20deg); }
  75% { transform: rotate(-10deg); }
}

.welcome-subtitle {
  font-size: var(--font-size-body);
  color: var(--color-text-tertiary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.stat-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  box-shadow: var(--shadow-card);
  transition: all var(--duration-short) var(--ease-out);
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-medium);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.stat-trend.up {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.stat-trend.down {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}

.stat-value {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.stat-title {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.stat-desc {
  font-size: var(--font-size-caption);
  color: var(--color-text-tertiary);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.chart-section,
.quick-actions {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  box-shadow: var(--shadow-card);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}

.section-title {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.section-actions {
  display: flex;
  gap: var(--space-xs);
}

.time-btn {
  padding: var(--space-xs) var(--space-sm);
  border: 1px solid var(--color-border-light);
  background: transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--duration-short) var(--ease-out);
}

.time-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.time-btn:hover:not(.active) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.trend-chart {
  width: 100%;
  height: 300px;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.action-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-primary);
  transition: all var(--duration-short) var(--ease-out);
}

.action-item:hover {
  background: var(--color-bg-page);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.action-text {
  flex: 1;
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
}

.action-arrow {
  color: var(--color-text-tertiary);
  font-size: 16px;
}

.recent-matches-section {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  box-shadow: var(--shadow-card);
}

.view-all {
  font-size: var(--font-size-body);
  color: var(--color-primary);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-weight: var(--font-weight-medium);
}

.view-all:hover {
  text-decoration: underline;
}

.matches-table {
  margin-top: var(--space-md);
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 2.5fr 1.5fr 2.5fr 1.5fr;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-bg-page);
  border-radius: var(--radius-md);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-xs);
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 2.5fr 1.5fr 2.5fr 1.5fr;
  padding: var(--space-md);
  border-radius: var(--radius-md);
  transition: background var(--duration-short) var(--ease-out);
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
}

.table-row:hover {
  background: var(--color-bg-page);
}

.table-row .col {
  display: flex;
  align-items: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-badge {
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
}

.score-high {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.score-medium {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.score-low {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.match-tag {
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
}

.no-tag {
  color: var(--color-text-tertiary);
}

.empty-matches {
  text-align: center;
  padding: var(--space-2xl);
  color: var(--color-text-tertiary);
}

.empty-matches p {
  margin: var(--space-md) 0;
  font-size: var(--font-size-body);
}

.empty-action {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

.empty-action:hover {
  text-decoration: underline;
}

@media (max-width: 992px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 2fr 2.5fr 1.5fr 2fr;
  }
  
  .col-tags {
    display: none;
  }
}

@media (max-width: 576px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-title {
    font-size: var(--font-size-h3);
  }
  
  .stat-value {
    font-size: var(--font-size-h2);
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    grid-template-columns: 1fr;
    gap: var(--space-xs);
    padding: var(--space-md);
    margin-bottom: var(--space-sm);
    background: var(--color-bg-page);
    border-radius: var(--radius-md);
  }
  
  .table-row .col::before {
    content: attr(data-label);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-tertiary);
    font-size: var(--font-size-caption);
    margin-right: var(--space-sm);
  }
}
</style>
