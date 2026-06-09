<template>
  <div class="job-analysis">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">岗位分析</h2>
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
                :value="job.id"
              />
            </el-select>
            <el-button type="primary" @click="analyzeJob" :disabled="!selectedJob">
              开始分析
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="selectedJob && analyzed" class="analysis-result">
        <div class="analysis-section">
          <h3 class="section-title">岗位需求树状图</h3>
          <div class="job-tree">
            <JobTree :jobId="selectedJob" />
          </div>
        </div>
      </div>

      <div v-else-if="selectedJob && !analyzed" class="empty-state">
        <el-empty description="请点击开始分析" />
      </div>
      <div v-else class="empty-state">
        <el-empty description="请选择岗位并点击开始分析" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import JobTree from '../components/JobTree.vue'
import { jobAbilityApi } from '../api/jobAbility'
import service from '../services/request'

const selectedJob = ref('')
const analyzed = ref(false)

const jobs = ref([])

// 从后端获取岗位列表
const fetchJobs = async () => {
  try {
    const response = await service.get('/job')
    if (response && Array.isArray(response)) {
      jobs.value = response.map(job => {
        return {
          id: job.id,
          job_name: job.job_name
        }
      })
    }
  } catch (error) {
    console.error('获取岗位列表失败:', error)
    ElMessage.error('获取岗位列表失败')
  }
}

const analyzeJob = async () => {
  try {
    const jobId = selectedJob.value
    console.log('分析岗位ID:', jobId);
    
    // 直接调用后端的岗位能力图谱创建接口
    const createResponse = await jobAbilityApi.createJobAbilityMap(jobId)
    console.log('创建岗位需求树响应:', createResponse);
    
    if (createResponse && (createResponse.data || createResponse)) {
      analyzed.value = true
      ElMessage.success('岗位分析完成')
    } else {
      throw new Error('无法生成岗位需求图谱')
    }
  } catch (error) {
    console.error('分析失败:', error)
    console.error('错误详情:', error.response?.data)
    ElMessage.error('分析失败，请重试')
  }
}

onMounted(() => {
  // 初始化时获取岗位列表
  fetchJobs()
})
</script>

<style scoped>
.job-analysis {
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

.job-selector {
  margin: var(--space-lg) 0;
}

.analysis-result {
  margin-top: var(--space-lg);
}

.analysis-section {
  margin-bottom: var(--space-xl);
}

.section-title {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-md);
}

.job-tree {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}



.job-radar {
  height: 400px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

.text-analysis {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

/* 能力维度分析 */
.analysis-card {
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: var(--font-size-h5);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.dimension-analysis {
  margin-top: var(--space-md);
}

.dimension-item {
  margin-bottom: var(--space-md);
  padding: var(--space-md);
  background: var(--color-bg-light);
  border-radius: var(--radius-md);
  transition: all 0.3s;
}

.dimension-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.dimension-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.dimension-score {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  background: var(--color-primary-light);
  padding: 2px 10px;
  border-radius: 12px;
}

.dimension-progress {
  margin: var(--space-sm) 0;
}

.dimension-details {
  margin-top: var(--space-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* 优劣势分析 */
.advantages-disadvantages {
  display: flex;
  gap: var(--space-md);
  margin: var(--space-md) 0;
}

.advantage-card,
.disadvantage-card {
  flex: 1;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.advantage-list,
.disadvantage-list {
  margin-top: var(--space-sm);
}

.advantage-item,
.disadvantage-item {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  transition: all 0.3s;
}

.advantage-item {
  background: var(--color-success-light);
  border-left: 4px solid var(--color-success);
}

.disadvantage-item {
  background: var(--color-danger-light);
  border-left: 4px solid var(--color-danger);
}

.advantage-item:hover,
.disadvantage-item:hover {
  box-shadow: var(--shadow-sm);
}

.advantage-icon {
  color: var(--color-success);
  margin-right: var(--space-sm);
  font-size: var(--font-size-base);
}

.disadvantage-icon {
  color: var(--color-danger);
  margin-right: var(--space-sm);
  font-size: var(--font-size-base);
}

/* 建议 */
.suggestion-card {
  border-radius: var(--radius-md);
}

.suggestion-list {
  margin-top: var(--space-sm);
}

.suggestion-item {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-sm);
  padding: var(--space-sm);
  background: var(--color-primary-light);
  border-radius: var(--radius-sm);
  transition: all 0.3s;
}

.suggestion-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateX(5px);
}

.suggestion-icon {
  color: var(--color-primary);
  margin-right: var(--space-sm);
  font-size: var(--font-size-base);
}

.empty-state {
  margin: var(--space-xl) 0;
  text-align: center;
}

@media screen and (max-width: 768px) {
  .advantages-disadvantages {
    flex-direction: column;
  }
  
  .dimension-item {
    padding: var(--space-sm);
  }
  
  .advantage-item,
  .disadvantage-item,
  .suggestion-item {
    padding: var(--space-xs) var(--space-sm);
  }
}
</style>