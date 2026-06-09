import { authAPI, userAPI } from '../api/index'
import { ElMessage } from 'element-plus'

class AuthService {
  // 登录
  async login(credentials) {
    try {
      const response = await authAPI.login(credentials)
      
      // 存储token和用户信息
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      localStorage.setItem('role', response.user.role)
      localStorage.setItem('roles', JSON.stringify(response.user.roles))
      
      return response
    } catch (error) {
      ElMessage.error('登录失败：' + (error.response?.data?.detail || error.message || '未知错误'))
      throw error
    }
  }
  
  // 登出
  async logout() {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      localStorage.removeItem('roles')
      ElMessage.success('登出成功')
    }
  }
  
  // 获取用户信息
  async profile() {
    try {
      const response = await userAPI.getInfo()
      // 更新本地存储的用户信息
      localStorage.setItem('user', JSON.stringify(response))
      // 更新本地存储的角色信息
      localStorage.setItem('role', response.role)
      localStorage.setItem('roles', JSON.stringify(response.roles))
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }
  
  // 检查是否已登录
  isAuthenticated() {
    return !!localStorage.getItem('token')
  }
  
  // 获取当前用户
  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
  
  // 获取当前角色
  getCurrentRole() {
    return localStorage.getItem('role') || 'job_seeker'
  }
  
  // 获取用户角色列表
  getUserRoles() {
    const rolesStr = localStorage.getItem('roles')
    if (rolesStr) {
      try {
        return JSON.parse(rolesStr)
      } catch (error) {
        console.error('解析角色失败:', error)
        // 如果解析失败，尝试从单个角色获取
        const role = this.getCurrentRole()
        return role ? [role] : ['job_seeker']
      }
    }
    // 如果没有roles，尝试从单个角色获取
    const role = this.getCurrentRole()
    return role ? [role] : ['job_seeker']
  }
  
  // 获取所有角色
  getAllRoles() {
    // 返回三种角色
    return ['job_seeker', 'company', 'admin']
  }
  
  // 切换角色
  switchRole(role) {
    const allRoles = this.getAllRoles()
    if (allRoles.includes(role)) {
      localStorage.setItem('role', role)
      // 同时更新 user 对象中的 role
      const user = this.getCurrentUser()
      if (user) {
        user.role = role
        localStorage.setItem('user', JSON.stringify(user))
      }
      return true
    }
    return false
  }
}
export const authService = new AuthService()