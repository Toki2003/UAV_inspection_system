import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 —— 自动附带 token
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 —— 统一错误处理
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
