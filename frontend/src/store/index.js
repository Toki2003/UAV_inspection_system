import { defineStore } from 'pinia'
import { ref } from 'vue'
import { triggerPermissionChange } from './permission'

export const useAppStore = defineStore('app', () => {
  const user = ref(null)
  const token = ref(null)
  const permissions = ref([])

  /**
   * 从 localStorage 恢复登录态（Token、用户信息、权限列表）
   * 应用初始化时调用
   */
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

  /**
   * 设置用户信息并持久化到 localStorage
   * @param {Object} userData - 用户对象
   */
  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  /**
   * 设置认证 Token 并持久化到 localStorage
   * @param {string} authToken - JWT Token
   */
  const setToken = (authToken) => {
    token.value = authToken
    localStorage.setItem('token', authToken)
  }

  /**
   * 设置用户权限列表并持久化，同时触发权限变更事件通知所有组件刷新
   * @param {Array} perms - 权限码列表
   */
  const setPermissions = (perms) => {
    permissions.value = perms || []
    localStorage.setItem('permissions', JSON.stringify(perms || []))
    // 触发权限变更事件，通知所有监听组件刷新 UI
    triggerPermissionChange()
  }

  /**
   * 清除所有登录态信息（Token、用户、权限），用于登出场景
   */
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