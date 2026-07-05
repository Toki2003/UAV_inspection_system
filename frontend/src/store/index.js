import { defineStore } from 'pinia'
import { ref } from 'vue'
import { triggerPermissionChange } from './permission'

export const useAppStore = defineStore('app', () => {
  const user = ref(null)
  const token = ref(null)
  const permissions = ref([])

  // 初始化（从本地恢复）
  const initAuth = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    const savedPermissions = localStorage.getItem('permissions')

    if (savedToken) token.value = savedToken

    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        user.value = null
      }
    }

    if (savedPermissions) {
      try {
        permissions.value = JSON.parse(savedPermissions)
      } catch {
        permissions.value = []
      }
    }
  }

  // 设置用户
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  // 设置 token
  const setToken = (authToken) => {
    token.value = authToken
    localStorage.setItem('token', authToken)
  }

  // 设置权限（重点）
  const setPermissions = (perms) => {
    permissions.value = perms || []
    localStorage.setItem('permissions', JSON.stringify(perms || []))
    // 触发权限变更事件，通知所有组件更新
    triggerPermissionChange()
  }

  // 清除登录信息
  const clearAuth = () => {
    user.value = null
    token.value = null
    permissions.value = []

    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('permissions')
  }

  return {
    user,
    token,
    permissions,
    setUser,
    setToken,
    setPermissions,
    clearAuth,
    initAuth
  }
})