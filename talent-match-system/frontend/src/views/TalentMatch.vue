<template>
  <div class="talent-match">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">人才匹配</h2>
        </div>
      </template>

      <div class="job-selector">
        <el-form label-width="80px">
          <el-form-item label="选择岗位">
            <el-select v-model="selectedJob" placeholder="请选择岗位">
              <el-option
                v-for="job in jobs"
                :key="job.id"
                :label="job.job_name"
                :value="job.id">
              </el-option>
            </el-select>
            <el-button type="primary" @click="matchTalents" :disabled="!selectedJob || isMatching" :loading="isMatching">
              {{ isMatching ? '匹配中...' : '开始匹配' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="matchResults.length > 0" class="match-results">
        <h3 class="section-title">匹配人才</h3>
        <el-table :data="matchResults" style="width: 100%">
          <el-table-column prop="name" label="姓名" width="100"></el-table-column>
          <el-table-column prop="position" label="应聘职位" width="150"></el-table-column>
          <el-table-column prop="desired_position" label="意向岗位" width="150"></el-table-column>
          <el-table-column prop="education" label="学历" width="100"></el-table-column>
          <el-table-column prop="experience" label="工作经验" width="120"></el-table-column>
          <el-table-column prop="matchScore" label="匹配度" width="100">
            <template #default="scope">
              <el-progress :percentage="Math.round(scope.row.matchScore)" :format="formatPercentage"></el-progress>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="320">
            <template #default="scope">
              <el-button size="small" @click="viewTalentDetail(scope.row)" style="margin-right: 8px;">查看详情</el-button>
              <el-button size="small" @click="viewMatchReason(scope.row)" style="margin-right: 8px;">匹配原因</el-button>
              <el-button size="small" type="primary" @click="sendInvitation(scope.row)">发送邀请</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="empty-state">
        <el-empty description="请选择岗位并点击开始匹配"></el-empty>
      </div>

      <el-dialog v-model="talentDetailDialog" :title="currentTalent?.name + ' - 详细信息'" width="600px">
        <div class="talent-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ currentTalent?.name }}</el-descriptions-item>
            <el-descriptions-item label="应聘职位">{{ currentTalent?.position }}</el-descriptions-item>
            <el-descriptions-item label="学历">{{ currentTalent?.education }}</el-descriptions-item>
            <el-descriptions-item label="工作经验">{{ currentTalent?.experience }}</el-descriptions-item>
            <el-descriptions-item label="技能">{{ currentTalent?.skills }}</el-descriptions-item>
            <el-descriptions-item label="自我评价">{{ currentTalent?.selfEvaluation }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="talentDetailDialog = false">关闭</el-button>
          </span>
        </template>
      </el-dialog>

      <el-dialog v-model="matchReasonDialog" title="匹配原因" width="500px">
        <div class="match-reason">{{ currentMatchReason }}</div>
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import service from '../services/request'
import { messageApi } from '../api/message'

const selectedJob = ref('')
const matchResults = ref([])
const talentDetailDialog = ref(false)
const matchReasonDialog = ref(false)
const currentTalent = ref(null)
const currentMatchReason = ref('')
const isMatching = ref(false)
const jobs = ref([])

const formatPercentage = (percentage) => {
  return `${percentage}%`
}

const fetchJobs = async () => {
  try {
    const response = await service.get('/job')
    jobs.value = response || []
  } catch (error) {
    console.error('获取岗位列表失败:', error)
    ElMessage.error('获取岗位列表失败')
  }
}

const fetchAllResumes = async () => {
  try {
    const response = await service.get('/resume/all')
    return response || []
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
    return []
  }
}

const matchTalents = async () => {
  if (!selectedJob.value) {
    ElMessage.error('请先选择岗位')
    return
  }
  
  if (isMatching.value) {
    return
  }
  
  isMatching.value = true
  
  try {
    ElMessage.info('正在进行人才匹配...')
    
    const resumes = await fetchAllResumes()
    if (!resumes || resumes.length === 0) {
      ElMessage.warning('暂无简历数据')
      return
    }
    
    const results = []
    for (const resume of resumes) {
      if (!resume || !resume.id) continue
      
      try {
        const matchResult = await service.post('/match', {
          resume_id: resume.id,
          job_id: selectedJob.value
        })
        
        const skills = Array.isArray(resume.skills) ? resume.skills : []
        
        let education = resume.education || resume.degree || ''
        if (!education && typeof resume.education === 'string' && resume.education.startsWith('{')) {
          try {
            const eduJson = JSON.parse(resume.education)
            education = eduJson.degree || eduJson.school || ''
          } catch (e) {}
        }
        
        let experience = resume.experience || ''
        let position = resume.position || resume.job_title || ''
        
        if (typeof resume.experience === 'string') {
          if (resume.experience.startsWith('[')) {
            try {
              const expArray = JSON.parse(resume.experience)
              if (Array.isArray(expArray) && expArray.length > 0) {
                const firstExp = expArray[0]
                if (firstExp.period) {
                  experience = firstExp.period
                } else if (firstExp.start_date && firstExp.end_date) {
                  experience = `${firstExp.start_date} - ${firstExp.end_date}`
                }
                if (!position && firstExp.position) {
                  position = firstExp.position
                }
              }
            } catch (e) {}
          } else if (resume.experience.startsWith('{')) {
            try {
              const expJson = JSON.parse(resume.experience)
              if (expJson && typeof expJson === 'object') {
                if (!experience || experience === '未知') {
                  experience = expJson.period || expJson.duration || ''
                }
                if (!position) {
                  position = expJson.position || expJson.company || ''
                }
              }
            } catch (e) {}
          }
        }
        
        results.push({
          id: resume.id,
          name: resume.name || '',
          position: position,
          desired_position: resume.desired_position || '',
          education: education,
          experience: experience,
          skills: skills.join(', ') || '',
          selfEvaluation: resume.self_evaluation || '',
          matchScore: matchResult.match_score || 0,
          matchReason: matchResult.career_advice || '匹配分析中...',
          matchStrengths: matchResult.match_strengths || [],
          matchGaps: matchResult.match_gaps || []
        })
      } catch (error) {
        console.error(`匹配简历 ${resume.id} 失败:`, error)
      }
    }
    
    matchResults.value = results.sort((a, b) => b.matchScore - a.matchScore)
    ElMessage.success('人才匹配完成')
  } catch (error) {
    ElMessage.error('人才匹配失败，请重试')
    console.error('人才匹配失败:', error)
  } finally {
    isMatching.value = false
  }
}

const viewTalentDetail = (talent) => {
  currentTalent.value = talent
  talentDetailDialog.value = true
}

const viewMatchReason = (talent) => {
  let reason = ''
  if (talent.matchStrengths && talent.matchStrengths.length > 0) {
    reason += '匹配优势：\n' + talent.matchStrengths.join('\n') + '\n\n'
  }
  if (talent.matchGaps && talent.matchGaps.length > 0) {
    reason += '待提升项：\n' + talent.matchGaps.join('\n') + '\n\n'
  }
  reason += talent.matchReason
  currentMatchReason.value = reason
  matchReasonDialog.value = true
}

const sendInvitation = async (talent) => {
  try {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    const companyId = user?.id || ''
    
    if (!companyId) {
      ElMessage.error('请先登录')
      return
    }
    
    const jobSeekerId = talent.id || ''
    if (!jobSeekerId) {
      ElMessage.error('无法获取求职者信息')
      return
    }
    
    await messageApi.createConversation(jobSeekerId, companyId, selectedJob.value, null)
    
    ElMessage.success(`已向${talent.name}发送诚聘邀请，请前往消息中心等待求职者确认`)
  } catch (error) {
    console.error('发送邀请失败:', error)
    ElMessage.error(error.response?.data?.detail || '发送邀请失败')
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.talent-match { padding: var(--space-lg); }
.page-card { border-radius: var(--radius-lg); box-shadow: var(--shadow-card); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.page-title { font-size: var(--font-size-h2); font-weight: var(--font-weight-bold); color: var(--color-text-primary); margin: 0; }
.job-selector { margin: var(--space-lg) 0; }
.match-results { margin-top: var(--space-lg); }
.section-title { font-size: var(--font-size-h4); font-weight: var(--font-weight-semibold); color: var(--color-text-primary); margin: 0 0 var(--space-md); }
.empty-state { margin: var(--space-xl) 0; text-align: center; }
.talent-detail { padding: var(--space-md); }
.match-reason { padding: var(--space-md); line-height: 1.6; color: var(--color-text-secondary); white-space: pre-wrap; }
</style>