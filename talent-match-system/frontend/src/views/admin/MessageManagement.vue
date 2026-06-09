<template>
  <div class="message-management">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2 class="page-title">系统消息管理</h2>
          <div class="card-actions">
            <el-button type="primary" @click="showTemplateModal = true">
              <el-icon name="plus" /> 新建模板
            </el-button>
          </div>
        </div>
      </template>

      <div class="tabs-container">
        <el-tabs v-model="activeTab" class="tabs">
          <el-tab-pane label="消息模板" name="templates">
            <div class="template-list">
              <div class="search-bar">
                <el-input 
                  v-model="templateSearch" 
                  placeholder="搜索模板名称..." 
                  prefix-icon="el-icon-search"
                  class="search-input"
                />
                <el-select v-model="templateCategory" placeholder="选择分类">
                  <el-option label="全部" value="" />
                  <el-option label="系统通知" value="system" />
                  <el-option label="简历相关" value="resume" />
                  <el-option label="岗位相关" value="job" />
                  <el-option label="匹配通知" value="match" />
                  <el-option label="警告提示" value="warning" />
                </el-select>
              </div>
              <el-table :data="templates" style="width: 100%">
                <el-table-column prop="name" label="模板名称" />
                <el-table-column prop="category" label="分类">
                  <template #default="scope">
                    <el-tag :type="getCategoryTagType(scope.row.category)">
                      {{ getCategoryLabel(scope.row.category) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="template_content" label="模板内容" show-overflow-tooltip />
                <el-table-column prop="is_active" label="状态">
                  <template #default="scope">
                    <el-switch 
                      :value="scope.row.is_active === 1" 
                      @change="toggleTemplateStatus(scope.row)"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="创建时间" />
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button size="small" @click="editTemplate(scope.row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="deleteTemplate(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="发送消息" name="send">
            <div class="send-message-form">
              <el-form :model="sendForm" label-width="120px">
                <el-form-item label="发送方式">
                  <el-radio-group v-model="sendForm.sendType">
                    <el-radio label="单个用户">单个用户</el-radio>
                    <el-radio label="多个用户">多个用户</el-radio>
                    <el-radio label="使用模板">使用模板</el-radio>
                  </el-radio-group>
                </el-form-item>

                <el-form-item v-if="sendForm.sendType === '单个用户'" label="用户ID">
                  <el-input v-model="sendForm.userId" placeholder="请输入用户ID" />
                </el-form-item>

                <el-form-item v-if="sendForm.sendType === '多个用户'" label="用户ID列表">
                  <el-input 
                    v-model="sendForm.userIds" 
                    type="textarea"
                    placeholder="请输入用户ID，每行一个"
                    :rows="4"
                  />
                </el-form-item>

                <el-form-item v-if="sendForm.sendType === '使用模板'" label="选择模板">
                  <el-select v-model="sendForm.templateId" placeholder="请选择模板">
                    <el-option 
                      v-for="template in activeTemplates" 
                      :key="template.id" 
                      :label="template.name" 
                      :value="template.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item v-if="sendForm.sendType !== '使用模板'" label="消息内容">
                  <el-input 
                    v-model="sendForm.content" 
                    type="textarea"
                    placeholder="请输入消息内容"
                    :rows="4"
                  />
                </el-form-item>

                <el-form-item v-if="sendForm.sendType === '使用模板'" label="模板变量">
                  <el-input 
                    v-model="sendForm.variables" 
                    placeholder='{"key": "value"}'
                  />
                </el-form-item>

                <el-form-item label="消息分类">
                  <el-select v-model="sendForm.category">
                    <el-option label="系统通知" value="system" />
                    <el-option label="简历相关" value="resume" />
                    <el-option label="岗位相关" value="job" />
                    <el-option label="匹配通知" value="match" />
                    <el-option label="警告提示" value="warning" />
                  </el-select>
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="sendMessage">发送消息</el-button>
                  <el-button @click="resetForm">重置</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <el-tab-pane label="消息记录" name="records">
            <div class="message-records">
              <div class="search-bar">
                <el-input 
                  v-model="recordSearch" 
                  placeholder="搜索消息内容..." 
                  prefix-icon="el-icon-search"
                  class="search-input"
                />
                <el-select v-model="recordCategory" placeholder="选择分类">
                  <el-option label="全部" value="" />
                  <el-option label="系统通知" value="system" />
                  <el-option label="简历相关" value="resume" />
                  <el-option label="岗位相关" value="job" />
                  <el-option label="匹配通知" value="match" />
                  <el-option label="警告提示" value="warning" />
                </el-select>
              </div>
              <el-table :data="systemMessages" style="width: 100%">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="user_id" label="用户ID" />
                <el-table-column prop="category" label="分类">
                  <template #default="scope">
                    <el-tag :type="getCategoryTagType(scope.row.category)">
                      {{ getCategoryLabel(scope.row.category) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="content" label="消息内容" show-overflow-tooltip />
                <el-table-column prop="is_read" label="状态">
                  <template #default="scope">
                    <el-tag :type="scope.row.is_read === 1 ? '' : 'primary'">
                      {{ scope.row.is_read === 1 ? '已读' : '未读' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="发送时间" />
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <el-dialog v-model="showTemplateModal" :title="editingTemplate ? '编辑模板' : '新建模板'" width="600px">
      <el-form :model="templateForm" label-width="120px">
        <el-form-item label="模板名称" required>
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="templateForm.category">
            <el-option label="系统通知" value="system" />
            <el-option label="简历相关" value="resume" />
            <el-option label="岗位相关" value="job" />
            <el-option label="匹配通知" value="match" />
            <el-option label="警告提示" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板内容" required>
          <el-input 
            v-model="templateForm.template_content" 
            type="textarea"
            placeholder="请输入模板内容，支持变量如 ${variable}"
            :rows="6"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" placeholder="请输入模板描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTemplateModal = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { messageApi } from '../../api/message'

const activeTab = ref('templates')
const templateSearch = ref('')
const templateCategory = ref('')
const recordSearch = ref('')
const recordCategory = ref('')

const templates = ref([])
const systemMessages = ref([])
const showTemplateModal = ref(false)
const editingTemplate = ref(null)

const templateForm = ref({
  name: '',
  category: 'system',
  template_content: '',
  description: ''
})

const sendForm = ref({
  sendType: '单个用户',
  userId: '',
  userIds: '',
  templateId: '',
  content: '',
  variables: '',
  category: 'system'
})

const activeTemplates = computed(() => {
  return templates.value.filter(t => t.is_active === 1)
})

const filteredTemplates = computed(() => {
  let result = templates.value
  if (templateSearch.value) {
    result = result.filter(t => t.name.toLowerCase().includes(templateSearch.value.toLowerCase()))
  }
  if (templateCategory.value) {
    result = result.filter(t => t.category === templateCategory.value)
  }
  return result
})

const filteredMessages = computed(() => {
  let result = systemMessages.value
  if (recordSearch.value) {
    result = result.filter(m => m.content.toLowerCase().includes(recordSearch.value.toLowerCase()))
  }
  if (recordCategory.value) {
    result = result.filter(m => m.category === recordCategory.value)
  }
  return result
})

const getCategoryLabel = (category) => {
  const categories = {
    system: '系统通知',
    resume: '简历相关',
    job: '岗位相关',
    match: '匹配通知',
    warning: '警告提示'
  }
  return categories[category] || category
}

const getCategoryTagType = (category) => {
  const types = {
    system: 'info',
    resume: 'success',
    job: 'primary',
    match: 'warning',
    warning: 'danger'
  }
  return types[category] || 'info'
}

const loadTemplates = async () => {
  try {
    const response = await messageApi.getSystemTemplates()
    templates.value = response.data.data || []
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

const loadSystemMessages = async () => {
  try {
    const response = await messageApi.getSystemMessages()
    systemMessages.value = response.data.data || []
  } catch (error) {
    console.error('加载消息记录失败:', error)
  }
}

const saveTemplate = async () => {
  if (!templateForm.value.name || !templateForm.value.template_content) {
    ElMessage.error('请填写必填项')
    return
  }

  try {
    if (editingTemplate.value) {
      await messageApi.updateSystemTemplate(editingTemplate.value.id, templateForm.value)
      ElMessage.success('模板更新成功')
    } else {
      await messageApi.createSystemTemplate(templateForm.value)
      ElMessage.success('模板创建成功')
    }
    showTemplateModal.value = false
    loadTemplates()
    resetTemplateForm()
  } catch (error) {
    ElMessage.error(editingTemplate.value ? '更新模板失败' : '创建模板失败')
  }
}

const editTemplate = (template) => {
  editingTemplate.value = template
  templateForm.value = {
    name: template.name,
    category: template.category,
    template_content: template.template_content,
    description: template.description || ''
  }
  showTemplateModal.value = true
}

const deleteTemplate = async (template) => {
  if (!confirm(`确定要删除模板「${template.name}」吗？`)) {
    return
  }
  try {
    await messageApi.deleteSystemTemplate(template.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const toggleTemplateStatus = async (template) => {
  try {
    await messageApi.updateSystemTemplate(template.id, {
      is_active: template.is_active === 1 ? 0 : 1
    })
    template.is_active = template.is_active === 1 ? 0 : 1
    ElMessage.success('状态更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
    template.is_active = template.is_active === 1 ? 0 : 1
  }
}

const resetTemplateForm = () => {
  templateForm.value = {
    name: '',
    category: 'system',
    template_content: '',
    description: ''
  }
  editingTemplate.value = null
}

const sendMessage = async () => {
  try {
    if (sendForm.value.sendType === '单个用户') {
      if (!sendForm.value.userId) {
        ElMessage.error('请输入用户ID')
        return
      }
      await messageApi.sendSystemMessage({
        user_id: sendForm.value.userId,
        content: sendForm.value.content,
        category: sendForm.value.category
      })
      ElMessage.success('消息发送成功')
    } else if (sendForm.value.sendType === '多个用户') {
      const userIds = sendForm.value.userIds.split('\n').filter(id => id.trim())
      if (userIds.length === 0) {
        ElMessage.error('请输入用户ID列表')
        return
      }
      await messageApi.sendSystemMessageToMultiple({
        user_ids: userIds,
        content: sendForm.value.content,
        category: sendForm.value.category
      })
      ElMessage.success(`消息已发送给 ${userIds.length} 个用户`)
    } else if (sendForm.value.sendType === '使用模板') {
      if (!sendForm.value.templateId) {
        ElMessage.error('请选择模板')
        return
      }
      const userIds = sendForm.value.userIds.split('\n').filter(id => id.trim())
      let variables = {}
      if (sendForm.value.variables) {
        try {
          variables = JSON.parse(sendForm.value.variables)
        } catch {
          ElMessage.error('变量格式不正确')
          return
        }
      }
      await messageApi.sendSystemMessageToMultiple({
        user_ids: userIds.length > 0 ? userIds : ['all'],
        template_id: sendForm.value.templateId,
        category: sendForm.value.category,
        variables
      })
      ElMessage.success('消息发送成功')
    }
    resetForm()
    loadSystemMessages()
  } catch (error) {
    ElMessage.error('发送失败')
  }
}

const resetForm = () => {
  sendForm.value = {
    sendType: '单个用户',
    userId: '',
    userIds: '',
    templateId: '',
    content: '',
    variables: '',
    category: 'system'
  }
}

onMounted(() => {
  loadTemplates()
  loadSystemMessages()
})
</script>

<style scoped>
.message-management {
  padding: 20px;
}

.page-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.tabs-container {
  margin-top: 20px;
}

.tabs {
  height: calc(100vh - 180px);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  width: 300px;
}

.template-list,
.send-message-form,
.message-records {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.el-form-item {
  margin-bottom: 16px;
}


</style>