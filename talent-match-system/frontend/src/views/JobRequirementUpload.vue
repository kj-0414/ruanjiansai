<template>
  <div class="job-requirement-upload">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">岗位需求材料上传</h2>
        </div>
      </template>

      <div class="upload-section">
        <h3 class="section-title">上传材料</h3>
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          accept=".pdf,.docx"
          :multiple="false"
          :file-list="uploadedFiles"
        >
          <el-button type="default">
            <el-icon><Upload /></el-icon>
            选择文件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 PDF 或 DOCX 文件
            </div>
          </template>
        </el-upload>
      </div>

      <div class="form-section">
        <el-form ref="formRef" :model="form" label-width="120px">
          <el-form-item label="岗位名称">
            <el-input v-model="form.job_name" placeholder="请输入岗位名称" />
          </el-form-item>
          <el-form-item label="公司名称">
            <el-input v-model="form.company_name" placeholder="请输入公司名称" />
          </el-form-item>
          <el-form-item label="公司规模">
            <el-select v-model="form.company_size" placeholder="请选择公司规模">
              <el-option label="小型企业" value="小型" />
              <el-option label="中型企业" value="中型" />
              <el-option label="大型企业" value="大型" />
              <el-option label="上市公司" value="上市" />
            </el-select>
          </el-form-item>
          <el-form-item label="公司行业">
            <el-input v-model="form.company_industry" placeholder="请输入公司所属行业" />
          </el-form-item>
          <el-form-item label="公司简介">
            <textarea v-model="form.company_intro" placeholder="请输入公司简介" rows="4" class="form-textarea" />
          </el-form-item>
        </el-form>
      </div>

      <div class="action-section">
        <el-button type="primary" @click="uploadJobRequirement" :loading="loading" :disabled="uploadedFiles.length === 0">
          <el-icon><Document /></el-icon>
          上传并分析
        </el-button>
      </div>

      <div class="job-list" v-if="jobs.length > 0">
        <h3 class="section-title">我的岗位</h3>
        <el-table :data="jobs" style="width: 100%">
          <el-table-column prop="job_name" label="岗位名称" width="200" />
          <el-table-column prop="salary" label="薪资" width="120" />
          <el-table-column prop="location" label="工作地点" width="150" />
          <el-table-column prop="education_requirement" label="学历要求" width="120" />
          <el-table-column prop="experience_requirement" label="工作经验" width="120" />
          <el-table-column prop="create_time" label="创建时间" width="200" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="viewJob(scope.row)">
                查看
              </el-button>
              <el-button size="small" type="danger" @click="deleteJob(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else-if="uploadedFiles.length === 0" class="empty-state">
        <el-empty description="请上传岗位需求材料" />
      </div>
    </el-card>

    <!-- 岗位查看对话框 -->
    <el-dialog
      v-model="jobPreviewDialog"
      :title="currentJob?.job_name"
      width="800px"
      fullscreen
    >
      <div class="job-preview">
        <div class="job-header">
          <h2>{{ currentJob?.job_name }}</h2>
          <p class="job-meta">
            创建时间：{{ currentJob?.create_time }} | 工作地点：{{ currentJob?.location || '未知' }}
          </p>
        </div>
        
        <div class="job-content">
          <div class="job-section">
            <h3>岗位信息</h3>
            <div class="job-info-item">
              <span class="label">薪资：</span>
              <span class="value">{{ currentJob?.salary || '未知' }}</span>
            </div>
            <div class="job-info-item">
              <span class="label">学历要求：</span>
              <span class="value">{{ currentJob?.education_requirement || '未知' }}</span>
            </div>
            <div class="job-info-item">
              <span class="label">工作经验：</span>
              <span class="value">{{ currentJob?.experience_requirement || '未知' }}</span>
            </div>
          </div>

          <div class="job-section">
            <h3>岗位描述</h3>
            <div class="job-description">
              {{ currentJob?.job_description || '暂无岗位描述' }}
            </div>
          </div>

          <div class="job-section">
            <h3>技能要求</h3>
            <div v-if="currentJob?.skills" class="skills-list">
              <span v-for="(skill, index) in currentJob?.skills" :key="index" class="skill-tag">
                {{ skill }}
              </span>
            </div>
            <div v-else class="empty-section">暂无技能要求信息</div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="jobPreviewDialog = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document } from '@element-plus/icons-vue'
import { jobAPI } from '../api'
import { useRouter } from 'vue-router'

const router = useRouter()
const formRef = ref(null)
const form = ref({
  job_name: '',
  company_name: '',
  company_size: '',
  company_industry: '',
  company_intro: ''
})

// 上传的材料文件列表
const uploadedFiles = ref([])
// 岗位列表
const jobs = ref([])
// 加载状态
const loading = ref(false)
// 岗位预览对话框
const jobPreviewDialog = ref(false)
// 当前查看的岗位
const currentJob = ref(null)

// 从后端获取岗位列表
const getJobs = async () => {
  try {
    const response = await jobAPI.getJobs()
    if (response) {
      // 转换后端返回的数据格式以匹配前端需要的格式
      jobs.value = response.map(job => {
        // 解析skills字段，从JSON字符串转换为数组
        let skills = []
        try {
          if (job.skills) {
            skills = JSON.parse(job.skills)
          }
        } catch (error) {
          console.error('解析skills失败:', error)
          skills = job.skills ? [job.skills] : []
        }
        
        return {
          id: job.id,
          job_name: job.job_name,
          salary: job.salary || '面议',
          location: job.location || '未知',
          education_requirement: job.education_requirement || '不限',
          experience_requirement: job.experience_requirement || '不限',
          create_time: job.create_time,
          job_description: job.job_description || '',
          skills: skills
        }
      })
    }
  } catch (error) {
    console.error('获取岗位列表失败:', error)
    ElMessage.error('获取岗位列表失败')
  }
}

onMounted(() => {
  // 组件挂载时获取岗位列表
  getJobs()
})

// 处理文件上传
const handleFileChange = (file, fileList) => {
  uploadedFiles.value = fileList
  console.log('文件列表:', uploadedFiles.value)
  ElMessage.success('材料上传成功')
}

// 处理文件移除
const handleFileRemove = (file) => {
  const index = uploadedFiles.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    uploadedFiles.value.splice(index, 1)
    ElMessage.success('材料移除成功')
  }
}

// 上传并分析岗位需求
const uploadJobRequirement = async () => {
  if (!form.value.job_name) {
    ElMessage.warning('请输入岗位名称')
    return
  }
  
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请选择文件')
    return
  }
  
  const file = uploadedFiles.value[0].raw
  const formData = new FormData()
  formData.append('job_name', form.value.job_name)
  formData.append('company_name', form.value.company_name)
  formData.append('company_size', form.value.company_size)
  formData.append('company_industry', form.value.company_industry)
  formData.append('company_intro', form.value.company_intro)
  formData.append('file', file)
  
  loading.value = true
  try {
    const response = await jobAPI.uploadJobRequirement(formData, form.value.job_name)
    ElMessage.success('岗位需求材料上传成功')
    
    form.value.job_name = ''
    form.value.company_name = ''
    form.value.company_size = ''
    form.value.company_industry = ''
    form.value.company_intro = ''
    uploadedFiles.value = []
    await getJobs()
    
    // 跳转到岗位分析页面
    router.push('/job-analysis')
  } catch (error) {
    if (error.response && error.response.status === 403) {
      ElMessage.error('权限不足，只有企业用户可以上传岗位需求材料')
    } else {
      ElMessage.error('岗位需求材料上传失败')
    }
    console.error('上传岗位需求失败:', error)
    console.error('错误详情:', error.response ? error.response.data : error.message)
  } finally {
    loading.value = false
  }
}

// 查看岗位
const viewJob = (job) => {
  currentJob.value = job
  jobPreviewDialog.value = true
}

// 删除岗位
const deleteJob = async (job) => {
  try {
    // 调用后端API删除岗位
    await jobAPI.deleteJob(job.id)
    
    // 重新获取岗位列表
    await getJobs()
    
    ElMessage.success('岗位删除成功')
  } catch (error) {
    console.error('删除岗位失败:', error)
    ElMessage.error('删除岗位失败')
  }
}
</script>

<style scoped>
.job-requirement-upload {
  padding: 20px;
}

.page-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.upload-section {
  margin: 20px 0;
}

.form-section {
  margin: 20px 0;
}

.action-section {
  margin: 20px 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 20px 0 10px;
}

.empty-state {
  margin: 40px 0;
  text-align: center;
}

/* 岗位预览样式 */
.job-preview {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
  background-color: white;
  min-height: 100vh;
}

.job-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.job-header h2 {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.job-meta {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.job-content {
  margin-top: 30px;
}

.job-section {
  margin-bottom: 30px;
}

.job-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.job-info-item {
  margin-bottom: 10px;
  display: flex;
}

.job-info-item .label {
  width: 100px;
  font-weight: 500;
  color: #606266;
}

.job-info-item .value {
  flex: 1;
  color: #303133;
}

.job-description {
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  text-align: justify;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  background-color: #ecf5ff;
  color: #409EFF;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
}

.empty-section {
  font-size: 14px;
  color: #909399;
  font-style: italic;
  padding-left: 20px;
}
</style>