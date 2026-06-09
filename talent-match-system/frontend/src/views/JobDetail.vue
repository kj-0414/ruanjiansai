<template>
  <div class="job-detail">
    <el-card class="page-card">
      <div class="card-header">
        <h2 class="page-title">{{ jobDetail.job_name }}</h2>
        <el-button @click="goBack" class="back-btn">
          返回
        </el-button>
      </div>
      
      <div class="job-info-grid">
        <div class="info-card">
          <div class="info-icon">💰</div>
          <div class="info-content">
            <span class="info-label">薪资</span>
            <span class="info-value">{{ jobDetail.salary || '面议' }}</span>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">📍</div>
          <div class="info-content">
            <span class="info-label">工作地点</span>
            <span class="info-value">{{ jobDetail.location || '未指定' }}</span>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">💼</div>
          <div class="info-content">
            <span class="info-label">工作经验</span>
            <span class="info-value">{{ jobDetail.experience || '不限' }}</span>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">🎓</div>
          <div class="info-content">
            <span class="info-label">学历要求</span>
            <span class="info-value">{{ jobDetail.education_level || '不限' }}</span>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">👥</div>
          <div class="info-content">
            <span class="info-label">招聘人数</span>
            <span class="info-value">{{ jobDetail.hiring_number || '若干' }}</span>
          </div>
        </div>
        <div class="info-card">
          <div class="info-icon">📋</div>
          <div class="info-content">
            <span class="info-label">岗位类型</span>
            <span class="info-value">{{ jobDetail.job_type || '全职' }}</span>
          </div>
        </div>
      </div>

      <div class="section">
        <h3 class="section-title">岗位描述</h3>
        <p class="section-content">{{ jobDetail.job_desc || '暂无描述' }}</p>
      </div>

      <!-- 公司信息 -->
      <div class="section">
        <h3 class="section-title">公司信息</h3>
        <div v-if="jobDetail.company_name" class="company-info">
          <div class="company-item">
            <span class="company-label">公司名称</span>
            <span class="company-value">{{ jobDetail.company_name }}</span>
          </div>
          <div class="company-item">
            <span class="company-label">公司性质</span>
            <span class="company-value">{{ jobDetail.company_type || '未填写' }}</span>
          </div>
          <div class="company-item">
            <span class="company-label">公司规模</span>
            <span class="company-value">{{ jobDetail.company_size || '未填写' }}</span>
          </div>
          <div class="company-item">
            <span class="company-label">所属行业</span>
            <span class="company-value">{{ jobDetail.company_industry || '未填写' }}</span>
          </div>
          <div class="company-intro">
            <span class="company-label">公司简介</span>
            <p class="company-intro-content">{{ jobDetail.company_intro || '暂无简介' }}</p>
          </div>
          <div v-if="companyTags.length > 0" class="company-tags">
            <span class="company-label">公司标签</span>
            <div class="tags-list">
              <span v-for="(tag, index) in companyTags" :key="index" class="tag-item">{{ tag }}</span>
            </div>
          </div>
        </div>
        <p v-else class="empty-text">暂无公司信息</p>
      </div>

      <!-- 福利待遇 -->
      <div class="section">
        <h3 class="section-title">福利待遇</h3>
        <div v-if="selectedBenefits.length > 0 || jobDetail.benefits" class="benefits-info">
          <div v-if="selectedBenefits.length > 0" class="benefits-list">
            <span v-for="(benefit, index) in selectedBenefits" :key="index" class="benefit-item">{{ benefit }}</span>
          </div>
          <div v-if="jobDetail.benefits" class="benefits-desc">
            <p>{{ jobDetail.benefits }}</p>
          </div>
        </div>
        <p v-else class="empty-text">暂无福利待遇信息</p>
      </div>

      <div class="section">
        <h3 class="section-title">技能要求</h3>
        <div v-if="jobSkills.length > 0" class="skills-list">
          <span v-for="(skill, index) in jobSkills" :key="index" class="skill-tag">{{ skill }}</span>
        </div>
        <p v-else class="empty-text">暂无技能要求</p>
      </div>

      <div class="section">
        <h3 class="section-title">证书要求</h3>
        <div v-if="jobCerts.length > 0" class="cert-list">
          <span v-for="(cert, index) in jobCerts" :key="index" class="cert-tag">{{ cert }}</span>
        </div>
        <p v-else class="empty-text">暂无证书要求</p>
      </div>

      <div class="section">
        <h3 class="section-title">项目经验要求</h3>
        <div v-if="jobProjects.length > 0" class="projects-list">
          <div v-for="(project, index) in jobProjects" :key="index" class="project-item">
            <div class="project-name">{{ project.name || '项目' + (index + 1) }}</div>
            <div v-if="project.domain" class="project-domain">领域：{{ project.domain }}</div>
            <div v-if="project.tech_stack && project.tech_stack.length > 0" class="project-tech">
              技术栈：{{ project.tech_stack.join(', ') }}
            </div>
          </div>
        </div>
        <p v-else class="empty-text">暂无项目经验要求</p>
      </div>

      <div class="section">
        <h3 class="section-title">岗位职责</h3>
        <p class="section-content">{{ jobDetail.responsibilities || '暂无职责描述' }}</p>
      </div>

      <div class="section">
        <h3 class="section-title">任职要求</h3>
        <p class="section-content">{{ jobDetail.requirements || '暂无任职要求' }}</p>
      </div>

      <div class="action-buttons">
        <el-button type="primary" @click="applyJob">申请此岗位</el-button>
        <el-button @click="goBack">返回列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import service from '../services/request'
import { messageApi } from '../api/message'

const route = useRoute()
const router = useRouter()
const jobDetail = ref({})
const jobSkills = ref([])
const jobCerts = ref([])
const jobProjects = ref([])
// 新增字段
const companyTags = ref([])
const selectedBenefits = ref([])

const goBack = () => {
  router.push('/job-match')
}

const fetchJobDetail = async () => {
  try {
    const jobId = route.params.id
    const response = await service.get(`/job/${jobId}`)
    jobDetail.value = response
    
    if (response.skills) {
      jobSkills.value = typeof response.skills === 'string' 
        ? JSON.parse(response.skills) 
        : response.skills
    }
    
    if (response.certificate_requirements) {
      jobCerts.value = typeof response.certificate_requirements === 'string' 
        ? JSON.parse(response.certificate_requirements) 
        : response.certificate_requirements
    }
    
    if (response.project_requirements) {
      jobProjects.value = typeof response.project_requirements === 'string' 
        ? JSON.parse(response.project_requirements) 
        : response.project_requirements
    }
    
    // 解析公司标签
    if (response.company_tags) {
      companyTags.value = typeof response.company_tags === 'string' 
        ? JSON.parse(response.company_tags) 
        : response.company_tags
    }
    
    // 解析福利待遇
    if (response.selected_benefits) {
      selectedBenefits.value = typeof response.selected_benefits === 'string' 
        ? JSON.parse(response.selected_benefits) 
        : response.selected_benefits
    }
  } catch (error) {
    console.error('获取岗位详情失败:', error)
    ElMessage.error('获取岗位详情失败')
  }
}

const applyJob = async () => {
  try {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    const jobSeekerId = user?.id || ''
    
    if (!jobSeekerId) {
      ElMessage.error('请先登录')
      return
    }
    
    const jobId = route.params.id
    const companyId = jobDetail.value.user_id || ''
    
    if (!companyId) {
      ElMessage.error('无法获取企业信息')
      return
    }
    
    await messageApi.createConversation(jobSeekerId, companyId, jobId, null)
    
    ElMessage.success(`已申请岗位：${jobDetail.value.job_name}，请前往消息中心等待企业确认`)
    router.push('/job-seeker/messages')
  } catch (error) {
    console.error('申请岗位失败:', error)
    ElMessage.error(error.response?.data?.detail || '申请岗位失败')
  }
}

onMounted(() => {
  fetchJobDetail()
})
</script>

<style scoped>
.job-detail {
  padding: var(--space-lg);
  max-width: 800px;
  margin: 0 auto;
}

.page-card {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: var(--space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.back-btn {
  padding: var(--space-sm) var(--space-md);
}

.job-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

.info-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
}

.info-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary-light);
  border-radius: var(--radius-sm);
}

.info-content {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.info-value {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.section {
  margin-bottom: var(--space-xl);
}

.section-title {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 2px solid var(--color-primary);
}

.section-content {
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.skills-list, .cert-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.skill-tag {
  padding: var(--space-xs) var(--space-md);
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

.cert-tag {
  padding: var(--space-xs) var(--space-md);
  background-color: var(--color-success-light);
  color: var(--color-success);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.project-item {
  padding: var(--space-md);
  background-color: var(--color-bg-light);
  border-radius: var(--radius-md);
}

.project-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-sm);
}

.project-domain, .project-tech {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xs);
}

.empty-text {
  color: var(--color-text-placeholder);
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  margin-top: var(--space-xl);
}

.action-buttons button {
  padding: var(--space-sm) var(--space-lg);
}
</style>