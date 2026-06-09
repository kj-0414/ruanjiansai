import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 从localStorage中获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // 从localStorage中获取角色信息
    const role = localStorage.getItem('role') || 'job_seeker'
    config.headers['X-Role'] = role
    
    console.log('=== 请求拦截器 ===')
    console.log('请求URL:', config.url)
    console.log('请求方法:', config.method)
    console.log('是否有token:', !!token)
    console.log('角色:', role)
    console.log('完整URL:', config.baseURL + config.url)
    
    // 设置Content-Type
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)
    console.error('Error config:', error.config)
    console.error('Error status:', error.response?.status)
    console.error('Error data:', error.response?.data)

    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      const isLoginPage = window.location.pathname === '/login'
      console.log('401 error, current path:', window.location.pathname)

      // 如果已经在登录页，不再跳转
      if (isLoginPage) {
        return Promise.reject(error)
      }

      // 检查是否是登录接口本身失败（这不应该触发跳转）
      const isAuthEndpoint = error.config?.url?.includes('/user/login') ||
                            error.config?.url?.includes('/user/register')
      if (isAuthEndpoint) {
        return Promise.reject(error)
      }

      // 清除登录信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      localStorage.removeItem('roles')

      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else if (error.response && error.response.status === 403) {
      ElMessage.error('权限不足')
    } else if (error.response && error.response.status === 404) {
      ElMessage.error('接口不存在')
    } else if (error.response && error.response.status === 500) {
      ElMessage.error('服务器内部错误')
    } else if (!error.response) {
      // 网络错误（如后端未启动）
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }

    return Promise.reject(error)
  }
)

// 添加delete方法
service.delete = (url, config) => {
  return service({
    method: 'delete',
    url,
    ...config
  })
}

export default service