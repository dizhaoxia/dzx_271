import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: '/',
  timeout: 30000,
})

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

service.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.detail || error.message || '请求失败'

    if (status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      ElMessage.warning('登录已过期，请重新登录')
      router.push('/login')
    } else if (status === 403) {
      ElMessage.error('权限不足')
    } else if (status === 400) {
      const errors = error.response?.data
      if (errors && typeof errors === 'object') {
        const firstKey = Object.keys(errors)[0]
        const firstMsg = errors[firstKey]
        ElMessage.error(Array.isArray(firstMsg) ? firstMsg[0] : String(firstMsg))
      } else {
        ElMessage.error(message)
      }
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.get(url, config) as Promise<T>
  },
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.post(url, data, config) as Promise<T>
  },
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.put(url, data, config) as Promise<T>
  },
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.patch(url, data, config) as Promise<T>
  },
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return service.delete(url, config) as Promise<T>
  },
}

export default service
