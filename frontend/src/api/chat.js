import apiClient from './client'

// 发送聊天消息
export const sendChatMessage = async (
  message,
  sessionId = null,
  documentIds = null,
  mode = 'kb',
) => {
  const response = await apiClient.post('/api/chat/', {
    message,
    session_id: sessionId,
    document_ids: documentIds,
    mode,
  })
  return response.data
}

// 获取聊天历史
export const getChatHistory = async (sessionId) => {
  const response = await apiClient.get(`/api/chat/history/${sessionId}`)
  return response.data
}

export const listChatSessions = async () => {
  const response = await apiClient.get('/api/chat/sessions')
  return response.data
}






