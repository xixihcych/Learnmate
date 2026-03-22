import apiClient, { uploadClient } from './client'

/**
 * OCR识别API
 */

// 简单OCR识别（只返回文本）
export const recognizeTextSimple = async (file, usePreprocess = true) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('use_preprocess', usePreprocess)
  
  const response = await uploadClient.post('/api/ocr/recognize-simple', formData)
  return response.data
}

// 详细OCR识别（返回完整信息）
export const recognizeText = async (file, usePreprocess = true) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('use_preprocess', usePreprocess)
  
  const response = await uploadClient.post('/api/ocr/recognize', formData)
  return response.data
}

// 批量OCR识别
export const recognizeTextBatch = async (files, usePreprocess = true) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  formData.append('use_preprocess', usePreprocess)
  
  const response = await uploadClient.post('/api/ocr/recognize-batch', formData)
  return response.data
}






