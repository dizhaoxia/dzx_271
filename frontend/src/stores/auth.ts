import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, Tokens } from '@/types'
import { request } from '@/utils/request'

const ACCESS_KEY = 'scl90_access_token'
const REFRESH_KEY = 'scl90_refresh_token'
const USER_KEY = 'scl90_user_info'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string>(localStorage.getItem(ACCESS_KEY) || '')
  const refreshToken = ref<string>(localStorage.getItem(REFRESH_KEY) || '')
  const userInfo = ref<User | null>(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isLoggedIn = computed(() => !!accessToken.value)
  const isStaff = computed(() => userInfo.value?.is_staff ?? false)

  function setTokens(tokens: Tokens) {
    accessToken.value = tokens.access
    refreshToken.value = tokens.refresh
    localStorage.setItem(ACCESS_KEY, tokens.access)
    localStorage.setItem(REFRESH_KEY, tokens.refresh)
  }

  function setUser(user: User) {
    userInfo.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  function clearAuth() {
    accessToken.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    localStorage.removeItem(USER_KEY)
  }

  async function login(phone: string, password: string) {
    const res: any = await request.post('/api/auth/login/', { phone, password })
    setTokens(res.tokens)
    setUser(res.user)
    return res
  }

  async function register(data: any) {
    const res: any = await request.post('/api/auth/register/', data)
    setTokens(res.tokens)
    setUser(res.user)
    return res
  }

  async function logout() {
    try {
      await request.post('/api/auth/logout/', { refresh: refreshToken.value })
    } finally {
      clearAuth()
    }
  }

  async function requestPasswordReset(phone: string) {
    return request.post('/api/auth/password-reset-request/', { phone })
  }

  async function confirmPasswordReset(data: any) {
    return request.post('/api/auth/password-reset-confirm/', data)
  }

  async function changePassword(oldPwd: string, newPwd: string) {
    return request.post('/api/auth/password/change/', {
      old_password: oldPwd,
      new_password: newPwd,
      confirm_password: newPwd,
    })
  }

  async function fetchProfile() {
    const user = await request.get<User>('/api/auth/profile/')
    setUser(user)
    return user
  }

  return {
    accessToken,
    refreshToken,
    userInfo,
    isLoggedIn,
    isStaff,
    login,
    register,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    fetchProfile,
    setTokens,
    setUser,
    clearAuth,
  }
})
