import apiClient from './client'

export const getKgStatistics = async () => {
  const response = await apiClient.get('/api/knowledge-graph/statistics')
  return response.data
}

export const buildKgFromDocuments = async () => {
  const response = await apiClient.post('/api/knowledge-graph/build-from-documents')
  return response.data
}

export const extractKgFromDocument = async (documentId) => {
  const response = await apiClient.post(`/api/knowledge-graph/extract-from-document/${documentId}`)
  return response.data
}

export const visualizeKg = async () => {
  const response = await apiClient.post('/api/knowledge-graph/visualize')
  return response.data
}

export const clearKg = async () => {
  const response = await apiClient.delete('/api/knowledge-graph/clear')
  return response.data
}

export const getKgTriples = async (limit = 100) => {
  const response = await apiClient.get(`/api/knowledge-graph/triples?format=json&limit=${limit}`)
  return response.data
}
