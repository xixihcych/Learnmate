import apiClient from './client'

export const registerUser = async (payload) => {
  const response = await apiClient.post('/api/auth/register', payload)
  return response.data
}

export const loginUser = async (payload) => {
  const response = await apiClient.post('/api/auth/login', payload)
  return response.data
}

export const resetPassword = async (payload) => {
  const response = await apiClient.post('/api/auth/reset-password', payload)
  return response.data
}
