import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const user = ref(null)
  const token = ref(null)

  const setUser = (userData) => {
    user.value = userData
  }

  const setToken = (authToken) => {
    token.value = authToken
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
  }

  return {
    user,
    token,
    setUser,
    setToken,
    clearAuth
  }
})
