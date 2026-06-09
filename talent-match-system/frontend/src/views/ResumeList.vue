<template>
  <div class="resume-list-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">我的简历管理</h1>
        <p class="page-subtitle">管理您的简历和草稿</p>
      </div>
      <el-button type="primary" size="large" @click="goToCreateResume">
        <el-icon><Plus /></el-icon> 新建简历
      </el-button>
    </div>

    <div class="tabs-wrapper">
      <el-tabs v-model="activeTab" type="card" class="resume-tabs">
        <el-tab-pane label="已保存简历" name="saved">
          <div v-if="savedResumes.length === 0" class="empty-state">
            <div class="empty-icon">📄</div>
            <p>暂无已保存的简历</p>
            <el-button type="primary" @click="goToCreateResume">立即创建</el-button>
          </div>
          <el-table v-else :data="savedResumes" border class="resume-table">
            <el-table-column prop="resume_name" label="简历名称" min-width="150">
              <template #default="scope">
                <span class="resume-name">{{ scope.row.resume_name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="school" label="毕业院校" width="150" />
            <el-table-column prop="degree" label="学历" width="80" />
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewResume(scope.row.id)">查看</el-button>
                <el-button size="small" type="primary" @click="editResume(scope.row.id)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteResume(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="草稿" name="draft">
          <div v-if="!draftExists" class="empty-state">
            <div class="empty-icon">📝</div>
            <p>暂无草稿</p>
            <el-button type="primary" @click="goToCreateResume">开始创建</el-button>
          </div>
          <div v-else class="draft-card">
            <div class="draft-header">
              <div class="draft-info">
                <div class="draft-icon">📝</div>
                <div>
                  <h3>简历草稿</h3>
                  <p class="draft-hint">上次保存于 {{ draftLastSaved }}</p>
                </div>
              </div>
              <div class="draft-actions">
                <el-button type="primary" @click="continueEdit">继续编辑</el-button>
                <el-button type="danger" @click="clearDraft">删除草稿</el-button>
              </div>
            </div>
            <div class="draft-preview">
              <div class="preview-row">
                <span class="preview-label">姓名:</span>
                <span>{{ draftData?.name || '未填写' }}</span>
              </div>
              <div class="preview-row">
                <span class="preview-label">电话:</span>
                <span>{{ draftData?.phone || '未填写' }}</span>
              </div>
              <div class="preview-row">
                <span class="preview-label">邮箱:</span>
                <span>{{ draftData?.email || '未填写' }}</span>
              </div>
              <div class="preview-row">
                <span class="preview-label">学校:</span>
                <span>{{ draftData?.school || '未填写' }}</span>
              </div>
              <div class="preview-row">
                <span class="preview-label">专业:</span>
                <span>{{ draftData?.major || '未填写' }}</span>
              </div>
              <div class="preview-row">
                <span class="preview-label">技能:</span>
                <span>{{ draftData?.skills?.length > 0 ? draftData.skills.join(', ') : '未填写' }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import service from '../services/request'

const router = useRouter()
const activeTab = ref('saved')
const savedResumes = ref([])

const draftData = computed(() => {
  const draft = localStorage.getItem('resumeDraft')
  if (draft) {
    try {
      return JSON.parse(draft)
    } catch (e) {
      return null
    }
  }
  return null
})

const draftExists = computed(() => {
  return draftData.value !== null
})

const draftLastSaved = computed(() => {
  const time = localStorage.getItem('resumeDraftTime')
  return time || '未知时间'
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const parseSkills = (skillsStr) => {
  try {
    const skills = JSON.parse(skillsStr)
    return Array.isArray(skills) ? skills : []
  } catch (e) {
    return skillsStr ? [skillsStr] : []
  }
}

const fetchResumes = async () => {
  try {
    const response = await service.get('/resume')
    if (response && Array.isArray(response)) {
      savedResumes.value = response
    }
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  }
}

const goToCreateResume = () => {
  router.push('/job-seeker/resume/create')
}

const viewResume = (resumeId) => {
  // 直接跳转到查看页面，通过 URL 参数传递 resumeId
  router.push(`/job-seeker/resume/create?resumeId=${resumeId}&view=true`)
}

const parseExperiences = (resume) => {
  const experiences = []
  // 解析工作经历
  const workExp = parseSkills(resume.work_experience)
  if (Array.isArray(workExp)) {
    workExp.forEach(exp => {
      if (typeof exp === 'object') {
        experiences.push({
          type: 'work',
          company: exp.company || '',
          position: exp.position || '',
          period: exp.period || '',
          description: exp.description || '',
          tech_stack: Array.isArray(exp.technologies) ? exp.technologies.join(', ') : (exp.tech_stack || '')
        })
      }
    })
  }
  // 解析实习经历
  const internExp = parseSkills(resume.internship_experience)
  if (Array.isArray(internExp)) {
    internExp.forEach(exp => {
      if (typeof exp === 'object') {
        experiences.push({
          type: 'internship',
          company: exp.company || '',
          position: exp.position || '',
          period: exp.period || '',
          description: exp.description || '',
          tech_stack: Array.isArray(exp.technologies) ? exp.technologies.join(', ') : (exp.tech_stack || '')
        })
      }
    })
  }
  // 解析项目经历
  const projects = parseSkills(resume.projects)
  if (Array.isArray(projects)) {
    projects.forEach(proj => {
      if (typeof proj === 'object') {
        experiences.push({
          type: 'project',
          company: proj.name || '',
          position: proj.domain || '',
          period: '',
          description: proj.description || '',
          tech_stack: Array.isArray(proj.technologies) ? proj.technologies.join(', ') : (proj.tech_stack || '')
        })
      }
    })
  }
  return experiences
}

const editResume = (resumeId) => {
  localStorage.removeItem('isViewMode') // 编辑模式
  router.push(`/job-seeker/resume/create?resumeId=${resumeId}`)
}

const deleteResume = async (resumeId) => {
  try {
    await ElMessageBox.confirm('确定要删除这份简历吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await service.delete(`/resume/${resumeId}`)
    ElMessage.success('删除成功')
    fetchResumes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const continueEdit = () => {
  router.push('/job-seeker/resume/create')
}

const clearDraft = () => {
  localStorage.removeItem('resumeDraft')
  localStorage.removeItem('resumeDraftTime')
  // 强制刷新页面以显示最新状态
  window.location.reload()
  ElMessage.success('草稿已删除')
}

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.resume-list-page { padding: 20px 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.header-content { flex: 1; }
.page-title { font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 0 0 8px 0; }
.page-subtitle { font-size: 14px; color: #666; margin: 0; }
.tabs-wrapper { background: #fff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 24px; }
.resume-tabs { margin-bottom: 20px; }
.empty-state { text-align: center; padding: 60px 20px; background: #f8f9fa; border-radius: 12px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state p { font-size: 16px; color: #666; margin: 0 0 20px 0; }
.resume-table { width: 100%; }
.resume-name { font-weight: 600; color: #1a1a1a; }
.draft-card { background: #fffbe6; border: 1px solid #ffe58f; border-radius: 12px; padding: 24px; }
.draft-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.draft-info { display: flex; align-items: center; gap: 12px; }
.draft-icon { font-size: 32px; }
.draft-info h3 { margin: 0 0 4px 0; font-size: 18px; font-weight: 600; }
.draft-hint { margin: 0; font-size: 12px; color: #999; }
.draft-preview { background: #fff; border-radius: 8px; padding: 16px; }
.preview-row { display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.preview-row:last-child { border-bottom: none; }
.preview-label { color: #999; width: 60px; flex-shrink: 0; }
</style>