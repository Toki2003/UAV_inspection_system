/**
 * 应用全局状态管理（Pinia Store）
 *
 * 职责：管理登录态（Token、用户信息、权限列表）的存储与刷新。
 * 设计决策：
 *   - localStorage 仅作为临时缓存，权限以后端为准
 *   - 权限变更时通过 triggerPermissionChange() 发布事件，通知所有组件刷新 UI
 *   - refreshPermissionsFromBackend() 确保角色编辑后前端权限立即同步
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { triggerPermissionChange } from './permission'

export const useAppStore = defineStore('app', () => {
  const user = ref(null)
  const token = ref(null)
  const permissions = ref([])

  /**
   * 从 localStorage 恢复登录态（Token、用户信息、权限列表）
   * 应用初始化时调用，仅作为临时缓存，后续会通过 refreshPermissionsFromBackend 从后端刷新
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
   * 从后端刷新当前用户权限（确保权限以后端为准）
   * 调用时机：应用启动、路由守卫验证 token、角色编辑 / 删除后
   */
  const refreshPermissionsFromBackend = async () => {
    if (!token.value) return false
    try {
      const res = await fetch('/api/system/userinfo', {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })
      if (!res.ok) return false
      const data = await res.json()
      if (data.code === 200 && data.data) {
        setUser(data.data)
        if (data.data.permissions) {
          setPermissions(data.data.permissions)
        }
        return true
      }
      return false
    } catch {
      return false
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
   * 设置用户权限列表并持久化，同时触发权限变更事件
   * @param {Array} perms - 权限码列表
   */
  const setPermissions = (perms) => {
    permissions.value = perms || []
    localStorage.setItem('permissions', JSON.stringify(perms || []))
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
    initAuth,
    refreshPermissionsFromBackend
  }
})