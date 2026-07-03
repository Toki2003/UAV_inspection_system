import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const user = ref(null)
  const token = ref(null)

  // 启动时从 localStorage 恢复登录状态
  const initAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken) token.value = savedToken
    if (savedUser) {
      try { user.value = JSON.parse(savedUser) } catch { /* ignore */ }
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const setToken = (authToken) => {
    token.value = authToken
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    user,
    token,
    setUser,
    setToken,
    clearAuth,
    initAuth
  }
})
