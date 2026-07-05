import axios from 'axios'
import { useAppStore } from '@/store'
import { expandPermissions } from '@/utils/permission'
import { ElMessage } from 'element-plus'

/**
 * API 路径与权限码的映射关系
 * 用于在请求发送前进行权限校验
 */
const API_PERMISSION_MAP = {
  // 角色管理
  'POST /system/roles/': 'role:create',
  'PUT /system/roles/*/': 'role:update',
  'DELETE /system/roles/*/': 'role:delete',
  
  // 用户管理
  'POST /system/users/': 'user:create',
  'PUT /system/users/*/': 'user:update',
  'DELETE /system/users/*/': 'user:delete',
  
  // 告警管理
  'POST /alert/': 'alert:handle',
  'PUT /alert/*/': 'alert:handle',
  'DELETE /alert/*/': 'alert:delete',
  
  // 无人机管控
  'POST /drone/': 'drone:control',
  'PUT /drone/*/': 'drone:control',
}

/**
 * 检查当前请求是否需要权限校验
 * @param {string} method - HTTP 方法
 * @param {string} url - 请求 URL
 * @returns {string|null} 需要的权限码，不需要则返回 null
 */
function getRequiredPermission(method, url) {
  const key = `${method.toUpperCase()} ${url}`
  
  // 精确匹配
  if (API_PERMISSION_MAP[key]) {
    return API_PERMISSION_MAP[key]
  }
  
  // 通配符匹配（处理带 ID 的路径）
  for (const [pattern, perm] of Object.entries(API_PERMISSION_MAP)) {
    const regex = new RegExp('^' + pattern.replace('*', '[^/]+') + '$')
    if (regex.test(key)) {
      return perm
    }
  }
  
  return null
}

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 * 自动附带 Authorization Token，并对写操作进行前端权限预校验
 */
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 权限校验
    const store = useAppStore()
    const permissions = expandPermissions(store.permissions || [])
    const requiredPerm = getRequiredPermission(config.method, config.url)
    
    if (requiredPerm && !permissions.includes(requiredPerm)) {
      ElMessage.error(`没有权限执行此操作（需要权限：${requiredPerm}）`)
      return Promise.reject(new Error(`Permission denied: ${requiredPerm}`))
    }
    
    return config
  },
  error => Promise.reject(error)
)

/**
 * 响应拦截器
 * 统一处理后端响应，拦截 401 状态并清除本地登录态
 */
instance.interceptors.response.use(
  response => {
    const data = response.data
    // 后端可能返回 HTTP 200 但 body 中 code 为 401（token 失效）
    if (data && data.code === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      window.location.href = '/login'
      return Promise.reject(new Error(data.message || '登录已过期，请重新登录'))
    }
    return data
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
      window.location.href = '/login'
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default instance
