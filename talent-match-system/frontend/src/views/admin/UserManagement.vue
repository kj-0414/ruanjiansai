<template>
  <div class="user-management">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
      <p class="page-description">管理平台用户账号</p>
    </div>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索手机号"
        class="search-input"
        @keyup.enter="searchUsers"
      >
        <template #append>
          <el-button @click="searchUsers">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <div class="user-table-container">
      <el-table :data="users" border :loading="loading">
        <el-table-column prop="id" label="用户ID" width="180">
          <template #default="scope">
            <span class="user-id">{{ scope.row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="150">
          <template #default="scope">
            <span>{{ scope.row.phone }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="roles" label="角色" width="200">
          <template #default="scope">
            <el-tag 
              v-for="role in scope.row.roles" 
              :key="role"
              :type="getRoleTagType(role)"
              size="small"
              class="role-tag"
            >
              {{ getRoleLabel(role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              size="small" 
              @click="editRoles(scope.row)"
              class="action-btn"
            >
              <el-icon><Edit /></el-icon>
              编辑角色
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="deleteUser(scope.row.id)"
              class="action-btn"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
          layout="prev, pager, next, jumper, ->, total"
        />
      </div>
    </div>
    
    <el-dialog title="编辑角色" :visible.sync="showEditModal" width="400px">
      <div class="role-edit-form">
        <p class="edit-user-info">用户: {{ editingUser?.phone }}</p>
        <el-checkbox-group v-model="selectedRoles">
          <el-checkbox label="job_seeker">求职者</el-checkbox>
          <el-checkbox label="company">企业</el-checkbox>
          <el-checkbox label="admin">管理员</el-checkbox>
        </el-checkbox-group>
      </div>
      <div class="dialog-footer" slot="footer">
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="saveRoles">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { adminAPI } from '../../api/admin'

const users = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showEditModal = ref(false)
const editingUser = ref(null)
const selectedRoles = ref([])

const loadUsers = async () => {
  loading.value = true
  try {
    const data = await adminAPI.getUsers(currentPage.value - 1, pageSize.value)
    if (data) {
      users.value = data.users || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const searchUsers = () => {
  currentPage.value = 1
  loadUsers()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadUsers()
}

const getRoleTagType = (role) => {
  const types = {
    job_seeker: '',
    company: 'success',
    admin: 'warning'
  }
  return types[role] || ''
}

const getRoleLabel = (role) => {
  const labels = {
    job_seeker: '求职者',
    company: '企业',
    admin: '管理员'
  }
  return labels[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const editRoles = (user) => {
  editingUser.value = user
  selectedRoles.value = [...user.roles]
  showEditModal.value = true
}

const saveRoles = async () => {
  if (!editingUser.value) return
  
  try {
    await adminAPI.updateUserRoles(editingUser.value.id, selectedRoles.value)
    ElMessage.success('角色更新成功')
    showEditModal.value = false
    loadUsers()
  } catch (error) {
    console.error('更新角色失败:', error)
    ElMessage.error('更新角色失败')
  }
}

const deleteUser = async (userId) => {
  if (!confirm('确定要删除该用户吗？')) return
  
  try {
    await adminAPI.deleteUser(userId)
    ElMessage.success('用户删除成功')
    loadUsers()
  } catch (error) {
    console.error('删除用户失败:', error)
    ElMessage.error('删除用户失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
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

.search-bar {
  margin-bottom: var(--space-lg);
}

.search-input {
  max-width: 400px;
}

.user-table-container {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.user-id {
  font-family: var(--font-mono);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.role-tag {
  margin-right: var(--space-xs);
}

.action-btn {
  margin-right: var(--space-xs);
}

.pagination-container {
  padding: var(--space-lg);
  display: flex;
  justify-content: flex-end;
}

.role-edit-form {
  padding: var(--space-md);
}

.edit-user-info {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-md) 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
}
</style>