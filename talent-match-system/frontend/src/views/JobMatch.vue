<template>
  <div class="job-match">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">岗位匹配</h2>
        </div>
      </template>

      <div class="resume-selector">
        <el-form label-width="80px">
          <el-form-item label="选择简历">
            <el-select v-model="selectedResume" placeholder="请选择简历">
              <el-option
                v-for="resume in resumes"
                :key="resume.id"
                :label="resume.name"
                :value="resume.id">
              </el-option>
            </el-select>
            <el-button type="primary" @click="matchJobs" :disabled="!selectedResume" :loading="isMatching">
              开始匹配
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="matchResults.length > 0" class="match-results">
        <h3 class="section-title">推荐岗位</h3>
        <el-table :data="matchResults" style="width: 100%">
          <el-table-column prop="jobTitle" label="岗位名称" width="200"></el-table-column>
          <el-table-column prop="companyName" label="公司名称" width="150"></el-table-column>
          <el-table-column prop="matchScore" label="匹配度" width="100">
            <template #default="scope">
              <el-progress :percentage="Math.round(scope.row.matchScore)" :format="formatPercentage"></el-progress>
            </template>
          </el-table-column>
          <el-table-column prop="salary" label="薪资" width="100"></el-table-column>
          <el-table-column prop="location" label="地点" width="100"></el-table-column>
          <el-table-column label="操作" width="260">
            <template #default="scope">
              <div class="action-buttons">
                <el-button 
                  size="small" 
                  icon="View" 
                  @click="viewJobDetail(scope.row)"
                  class="action-btn detail-btn"
                >
                  查看详情
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  icon="Send" 
                  @click="handleApplyOrInvite(scope.row)"
                  class="action-btn primary-btn"
                >
                  {{ isJobSeeker ? '投递简历' : '岗位邀请' }}
                </el-button>
                <el-button 
                  size="small" 
                  type="info" 
                  icon="HelpFilled" 
                  @click="viewMatchReason(scope.row)"
                  class="action-btn reason-btn"
                >
                  匹配原因
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="empty-state">
        <el-empty description="请选择简历并点击开始匹配"></el-empty>
      </div>

      <!-- 匹配原因对话框 -->
      <el-dialog
        v-model="matchReasonDialog"
        title="匹配原因分析"
        width="600px"
        :before-close="() => matchReasonDialog = false"
      >
        <div class="match-reason-container">
          <!-- 匹配优势 -->
          <div class="match-section">
            <div class="section-header success">
              <span class="section-icon">✓</span>
              <span class="section-title">匹配优势</span>
            </div>
            <div class="section-content">
              <div 
                v-for="(item, index) in matchStrengths" 
                :key="index" 
                class="match-tag success"
              >
                {{ item }}
              </div>
              <div v-if="matchStrengths.length === 0" class="empty-text">暂无匹配优势</div>
            </div>
          </div>

          <!-- 待提升项 -->
          <div class="match-section">
            <div class="section-header warning">
              <span class="section-icon">!</span>
              <span class="section-title">待提升项</span>
            </div>
            <div class="section-content">
              <div 
                v-for="(item, index) in matchGaps" 
                :key="index" 
                class="match-tag warning"
              >
                {{ item }}
              </div>
              <div v-if="matchGaps.length === 0" class="empty-text">暂无待提升项</div>
            </div>
          </div>

          <!-- 职业建议 -->
          <div class="match-section">
            <div class="section-header info">
              <span class="section-icon">💡</span>
              <span class="section-title">职业建议</span>
            </div>
            <div class="section-content advice">
              {{ careerAdvice }}
            </div>
          </div>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="matchReasonDialog = false">关闭</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import service from '../services/request'

const router = useRouter()
const selectedResume = ref('')
const matchResults = ref([])
const matchReasonDialog = ref(false)
const currentMatchReason = ref('')
const isMatching = ref(false)

const resumes = ref([])

const currentRole = computed(() => {
  return localStorage.getItem('role') || 'job_seeker'
})

const isJobSeeker = computed(() => currentRole.value === 'job_seeker')

// 匹配原因数据
const matchStrengths = ref([])
const matchGaps = ref([])
const careerAdvice = ref('')

const formatPercentage = (percentage) => {
  return `${percentage}%`
}

// 获取简历列表
const fetchResumes = async () => {
  try {
    const response = await service.get('/resume')
    resumes.value = response
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  }
}

// 岗位匹配
const matchJobs = async () => {
  if (!selectedResume.value) {
    ElMessage.error('请先选择简历')
    return
  }

  isMatching.value = true
  ElMessage.info('正在进行岗位匹配...')

  try {
    // 获取所有岗位
    const jobs = await service.get('/job')
    
    // 对每个岗位进行匹配
    const results = []
    for (const job of jobs) {
      try {
        const matchResult = await service.post('/match', {
          resume_id: selectedResume.value,
          job_id: job.id
        })
        
        results.push({
          id: job.id,
          jobTitle: job.job_name,
          companyName: '企业用户',
          matchScore: matchResult.match_score || 0,
          salary: job.salary || '',
          location: job.location || '',
          matchReason: matchResult.career_advice || '匹配分析中...',
          matchStrengths: matchResult.match_strengths || [],
          matchGaps: matchResult.match_gaps || []
        })
      } catch (error) {
        console.error(`匹配岗位 ${job.id} 失败:`, error)
      }
    }

    // 按匹配度排序
    matchResults.value = results.sort((a, b) => b.matchScore - a.matchScore)
    ElMessage.success('岗位匹配完成')
  } catch (error) {
    ElMessage.error('岗位匹配失败，请重试')
    console.error('岗位匹配失败:', error)
  } finally {
    isMatching.value = false
  }
}

const viewJobDetail = (job) => {
  router.push(`/job-detail/${job.id}`)
}

const handleApplyOrInvite = async (job) => {
  if (!selectedResume.value) {
    ElMessage.error('请先选择简历')
    return
  }

  try {
    if (isJobSeeker.value) {
      await service.post('/match/deliver', {
        resume_id: selectedResume.value,
        job_id: job.id
      })
      ElMessage.success(`投递简历成功！会话已创建`)
    } else {
      ElMessage.success(`已发送岗位邀请：${job.jobTitle}`)
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
    console.error('投递失败:', error)
  }
}

const viewMatchReason = (job) => {
  // 设置匹配优势
  if (job.matchStrengths && job.matchStrengths.length > 0) {
    matchStrengths.value = job.matchStrengths
  } else {
    matchStrengths.value = []
  }
  
  // 设置待提升项
  if (job.matchGaps && job.matchGaps.length > 0) {
    matchGaps.value = job.matchGaps
  } else {
    matchGaps.value = []
  }
  
  // 设置职业建议
  if (job.matchReason) {
    careerAdvice.value = job.matchReason
  } else {
    careerAdvice.value = '暂无职业建议'
  }
  
  matchReasonDialog.value = true
}

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.job-match {
  padding: var(--space-lg);
}

.page-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.resume-selector {
  margin: var(--space-lg) 0;
}

.match-results {
  margin-top: var(--space-lg);
}

.section-title {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-md);
}

.empty-state {
  margin: var(--space-xl) 0;
  text-align: center;
}

.match-reason {
  padding: var(--space-md);
  line-height: 1.6;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
}

.match-reason-container {
  padding: var(--space-sm);
}

.match-section {
  margin-bottom: var(--space-lg);
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
}

.section-header.success {
  background-color: rgba(103, 194, 57, 0.1);
  color: #67c23a;
}

.section-header.warning {
  background-color: rgba(250, 173, 20, 0.1);
  color: #e6a23c;
}

.section-header.info {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.section-icon {
  margin-right: var(--space-sm);
  font-size: var(--font-size-lg);
}

.section-title {
  font-size: var(--font-size-base);
}

.section-content {
  padding: var(--space-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  min-height: 80px;
}

.section-content.advice {
  line-height: 1.8;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.match-tag {
  display: inline-block;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  margin-right: var(--space-sm);
  margin-bottom: var(--space-sm);
  font-size: var(--font-size-sm);
}

.match-tag.success {
  background-color: rgba(103, 194, 57, 0.15);
  color: #67c23a;
}

.match-tag.warning {
  background-color: rgba(250, 173, 20, 0.15);
  color: #e6a23c;
}

.empty-text {
  color: var(--color-text-placeholder);
  font-size: var(--font-size-sm);
}

.action-buttons {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: nowrap;
  justify-content: flex-start;
  padding: 4px 0;
}

.action-btn {
  flex-shrink: 0;
  border-radius: 6px;
  transition: all 0.2s ease;
  height: 28px;
  line-height: 28px;
  padding: 0 10px;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-btn:active {
  transform: translateY(0);
}

.detail-btn {
  background: #f5f7fa;
  border-color: #e4e7ed;
  color: #606266;
}

.detail-btn:hover {
  background: #eef2f7;
  border-color: #dcdfe6;
}

.primary-btn {
  background: linear-gradient(135deg, #409EFF 0%, #66B2FF 100%);
  border: none;
  color: #fff;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #66B2FF 0%, #8CC5FF 100%);
}

.reason-btn {
  background: linear-gradient(135deg, #5EB87A 0%, #7ED397 100%);
  border: none;
  color: #fff;
}

.reason-btn:hover {
  background: linear-gradient(135deg, #7ED397 0%, #A8E8BC 100%);
}
</style>