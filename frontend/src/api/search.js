import apiClient from './client'

// 语义搜索
export const semanticSearch = async (query, topK = 5, documentIds = null) => {
  const response = await apiClient.post('/api/search/', {
    query,
    top_k: topK,
    document_ids: documentIds,
  })
  return response.data
}






