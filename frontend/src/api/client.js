import axios from 'axios'

// 优先使用 Vite 代理（同源 /api -> 后端），避免前端端口变化导致 CORS 拉取失败。
// 如需直连后端（不走代理），再通过 VITE_API_BASE_URL 显式指定，例如：http://127.0.0.1:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 文件上传客户端
export const uploadClient = axios.create({
  baseURL: API_BASE_URL,
  // 不要手动设置 multipart/form-data；让 axios 自动补齐 boundary，避免后端解析失败/浏览器报网络错误
})

uploadClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default apiClient






