import apiClient, { uploadClient } from './client'

// 上传文件
export const uploadFile = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  // 显式开启上传后自动处理；图片会走 OCR 提取并入知识库
  formData.append('auto_process', 'true')
  formData.append('use_ocr_preprocess', 'true')
  
  const response = await uploadClient.post('/api/upload/', formData)
  return response.data
}

// 获取文档列表
export const getDocuments = async () => {
  const response = await apiClient.get('/api/document/')
  return response.data
}

// 获取文档详情
export const getDocument = async (documentId) => {
  const response = await apiClient.get(`/api/document/${documentId}`)
  return response.data
}

// 获取文档解析后的可复制文本（预览用）
export const getDocumentText = async (documentId) => {
  const response = await apiClient.get(`/api/document/${documentId}/text`)
  return response.data
}

// 删除文档
export const deleteDocument = async (documentId) => {
  const response = await apiClient.delete(`/api/document/${documentId}`)
  return response.data
}

// 处理文档（解析并添加到知识库）
export const processDocument = async (documentId) => {
  const response = await apiClient.post(`/api/process/document/${documentId}`)
  return response.data
}

