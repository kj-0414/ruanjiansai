import { authService } from '../services/auth'
import { ElMessage } from 'element-plus'

export const setupRouterGuard = (router) => {
  router.beforeEach(async (to, from, next) => {
    console.log('[Router Guard] 路由跳转:', from.path, '->', to.path)
    
    const whiteList = ['/login', '/register']
    
    if (whiteList.includes(to.path)) {
      console.log('[Router Guard] 白名单路由，直接通过')
      next()
      return
    }
    
    if (!authService.isAuthenticated()) {
      console.log('[Router Guard] 未认证，跳转到登录页')
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    const currentRole = authService.getCurrentRole()
    console.log('[Router Guard] 当前角色:', currentRole)
    
    if (to.path.startsWith('/admin')) {
      if (currentRole !== 'admin') {
        console.log('[Router Guard] 权限不足，需要管理员权限')
        ElMessage.error('权限不足，需要管理员权限')
        if (currentRole === 'job_seeker') {
          next('/job-seeker/home')
        } else if (currentRole === 'company') {
          next('/company/home')
        } else {
          next('/job-seeker/home')
        }
        return
      }
    } else if (to.path.startsWith('/job-seeker')) {
      if (currentRole !== 'job_seeker') {
        console.log('[Router Guard] 权限不足，需要求职者权限')
        ElMessage.error('权限不足，需要求职者权限')
        if (currentRole === 'company') {
          next('/company/home')
        } else if (currentRole === 'admin') {
          next('/admin/dashboard')
        } else {
          next('/company/home')
        }
        return
      }
    } else if (to.path.startsWith('/company')) {
      if (currentRole !== 'company') {
        console.log('[Router Guard] 权限不足，需要企业权限')
        ElMessage.error('权限不足，需要企业权限')
        if (currentRole === 'job_seeker') {
          next('/job-seeker/home')
        } else if (currentRole === 'admin') {
          next('/admin/dashboard')
        } else {
          next('/job-seeker/home')
        }
        return
      }
    }
    
    console.log('[Router Guard] 路由验证通过')
    next()
  })
  
  router.afterEach(() => {
  })
}