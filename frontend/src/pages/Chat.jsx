import React, { useState, useEffect, useRef } from 'react'
import { Card, Input, Button, List, Avatar, Typography, Space, Tag, Select, Upload, message } from 'antd'
import { SendOutlined, UserOutlined, RobotOutlined, ScanOutlined } from '@ant-design/icons'
import { getChatHistory, listChatSessions, sendChatMessage } from '../api/chat'
import { getDocuments } from '../api/document'
import { recognizeText } from '../api/ocr'

const { TextArea } = Input
const { Text, Paragraph } = Typography

const Chat = () => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [documents, setDocuments] = useState([])
  const [mode, setMode] = useState('kb')
  const [selectedDocumentIds, setSelectedDocumentIds] = useState([])
  const [sessions, setSessions] = useState([])
  const [ocrLoading, setOcrLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    // 加载文档列表
    getDocuments().then(setDocuments).catch(console.error)
    // 加载会话列表
    listChatSessions().then(setSessions).catch(() => setSessions([]))
  }, [])

  useEffect(() => {
    // 滚动到底部
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (!sessionId) return
    getChatHistory(sessionId)
      .then((res) => {
        const historyMessages = []
        for (const item of res.history || []) {
          historyMessages.push({
            role: 'user',
            content: item.user,
            timestamp: item.timestamp ? new Date(item.timestamp) : new Date(),
          })
          historyMessages.push({
            role: 'assistant',
            content: item.ai,
            timestamp: item.timestamp ? new Date(item.timestamp) : new Date(),
          })
        }
        setMessages(historyMessages)
      })
      .catch(() => {
        // ignore
      })
  }, [sessionId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage = inputValue.trim()
    setInputValue('')
    
    // 添加用户消息
    const newUserMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newUserMessage])
    setLoading(true)

    try {
      const response = await sendChatMessage(
        userMessage,
        sessionId,
        selectedDocumentIds.length > 0 ? selectedDocumentIds : null,
        mode,
      )
      
      // 更新sessionId
      if (response.session_id) {
        setSessionId(response.session_id)
      }
      // 刷新会话列表
      listChatSessions().then(setSessions).catch(() => setSessions([]))

      // 添加AI回复
      const aiMessage = {
        role: 'assistant',
        content: response.response,
        sources: response.sources || [],
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `错误: ${error.response?.data?.detail || error.message}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleOcrToInput = async (file) => {
    setOcrLoading(true)
    try {
      const res = await recognizeText(file, true)
      const ocrText = (res?.text || '').trim()
      if (!ocrText) {
        message.warning('未识别到有效文字，请换一张更清晰的图片')
        return false
      }
      setInputValue((prev) => (prev?.trim() ? `${prev}\n${ocrText}` : ocrText))
      message.success('OCR文字已填入输入框，请确认后发送')
    } catch (error) {
      message.error(`OCR失败: ${error.response?.data?.detail || error.message}`)
    } finally {
      setOcrLoading(false)
    }
    return false
  }

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'flex', gap: '16px' }}>
      <Card style={{ width: 320, flex: '0 0 320px' }} title="会话记录">
        <Space style={{ marginBottom: 12 }}>
          <Button
            onClick={() => {
              setSessionId(null)
              setMessages([])
            }}
          >
            新建会话
          </Button>
        </Space>
        <List
          size="small"
          dataSource={sessions}
          locale={{ emptyText: '暂无会话' }}
          renderItem={(s) => (
            <List.Item
              style={{
                cursor: 'pointer',
                background: s.session_id === sessionId ? '#e6f4ff' : 'transparent',
                borderRadius: 8,
                padding: '8px 10px',
              }}
              onClick={() => setSessionId(s.session_id)}
            >
              <div style={{ width: '100%' }}>
                <div style={{ fontSize: 12, color: '#666' }}>{s.last_timestamp || ''}</div>
                <div style={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.last_user_message || s.last_ai_response || s.session_id}
                </div>
              </div>
            </List.Item>
          )}
        />
      </Card>

      <Card style={{ flex: 1 }}>
        <div
          style={{
            height: '600px',
            overflowY: 'auto',
            padding: '20px',
            background: '#fafafa',
            borderRadius: '8px',
            marginBottom: '20px',
          }}
        >
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              <RobotOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
              <Paragraph>开始提问吧！我会基于您的文档知识库为您解答。</Paragraph>
            </div>
          ) : (
            <List
              dataSource={messages}
              renderItem={(item, index) => (
                <List.Item
                  key={index}
                  style={{
                    justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start',
                    padding: '12px 0',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: item.role === 'user' ? 'row-reverse' : 'row',
                      alignItems: 'flex-start',
                      gap: '12px',
                      maxWidth: '80%',
                    }}
                  >
                    <Avatar
                      icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      style={{
                        backgroundColor: item.role === 'user' ? '#1890ff' : '#52c41a',
                      }}
                    />
                    <div
                      style={{
                        background: item.role === 'user' ? '#1890ff' : '#fff',
                        color: item.role === 'user' ? '#fff' : '#000',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      }}
                    >
                      <Paragraph
                        style={{
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                        }}
                      >
                        {item.content}
                      </Paragraph>
                      {item.sources && item.sources.length > 0 && (
                        <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.2)' }}>
                          <Text style={{ fontSize: '12px', opacity: 0.8 }}>来源：</Text>
                          <Space size="small" wrap>
                            {item.sources.map((source, idx) => (
                              <Tag key={idx} style={{ fontSize: '11px' }}>
                                {source.filename}
                              </Tag>
                            ))}
                          </Space>
                        </div>
                      )}
                    </div>
                  </div>
                </List.Item>
              )}
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        <Space.Compact style={{ width: '100%' }}>
          <div style={{ marginBottom: '12px', width: '100%' }}>
            <Space wrap>
              <Select
                value={mode}
                onChange={setMode}
                style={{ width: 220 }}
                options={[
                  { value: 'kb', label: 'KB 模式（仅读取知识库）' },
                  { value: 'hybrid', label: 'Hybrid 模式（知识库 + DeepSeek）' },
                ]}
              />
              <Select
                mode="multiple"
                allowClear
                placeholder="可选：限制到指定文档"
                style={{ minWidth: 320 }}
                value={selectedDocumentIds}
                onChange={setSelectedDocumentIds}
                options={documents.map((doc) => ({
                  value: doc.id,
                  label: `${doc.id} - ${doc.filename}`,
                }))}
              />
              <Upload
                accept=".jpg,.jpeg,.png,.bmp,.webp,.tiff,.tif,.gif"
                beforeUpload={handleOcrToInput}
                showUploadList={false}
                disabled={loading || ocrLoading}
              >
                <Button icon={<ScanOutlined />} loading={ocrLoading} disabled={loading}>
                  OCR提取到输入框
                </Button>
              </Upload>
            </Space>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持扫描试卷/拍照讲义/截图；OCR仅回填输入框，不会自动发送。
            </div>
          </div>
        </Space.Compact>

        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={mode === 'kb' ? '输入知识库问题...' : '输入专项任务（将结合知识库与DeepSeek）...'}
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            style={{ height: 'auto' }}
          >
            发送
          </Button>
        </Space.Compact>
      </Card>
    </div>
  )
}

export default Chat






