import React, { useState } from 'react'
import { Card, Upload, Button, message, Typography, Space } from 'antd'
import { UploadOutlined, FileTextOutlined, MessageOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { uploadFile } from '../api/document'

const { Title, Paragraph } = Typography

const Home = () => {
  const navigate = useNavigate()
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (file) => {
    setUploading(true)
    try {
      const result = await uploadFile(file)
      message.success(result?.message || `文件 ${file.name} 上传成功！`)
      // 跳转到文档管理页面
      setTimeout(() => {
        navigate('/documents')
      }, 1000)
    } catch (error) {
      message.error(`上传失败: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
    return false // 阻止自动上传
  }

  return (
    <div style={{ padding: '40px 0' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <Title level={1}>欢迎使用 LearnMate</Title>
        <Paragraph style={{ fontSize: '18px', color: '#666' }}>
          AI驱动的智能学习助手，帮助您更好地管理和学习文档
        </Paragraph>
      </div>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Title level={3}>
              <UploadOutlined /> 上传文档
            </Title>
            <Paragraph>
              支持 PDF、Word、PPT 以及常见图片格式。上传后可解析文本并进入知识库。
            </Paragraph>
            <Upload
              accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.bmp,.webp,.tiff,.tif,.gif"
              beforeUpload={handleUpload}
              showUploadList={false}
            >
              <Button type="primary" size="large" loading={uploading} icon={<UploadOutlined />}>
                选择文件上传
              </Button>
            </Upload>
          </Space>
        </Card>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          <Card hoverable onClick={() => navigate('/documents')} style={{ cursor: 'pointer' }}>
            <Space direction="vertical" size="middle">
              <FileTextOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
              <Title level={4}>文档管理</Title>
              <Paragraph>查看和管理已上传的文档，支持文档预览和删除</Paragraph>
            </Space>
          </Card>

          <Card hoverable onClick={() => navigate('/chat')} style={{ cursor: 'pointer' }}>
            <Space direction="vertical" size="middle">
              <MessageOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
              <Title level={4}>AI问答</Title>
              <Paragraph>基于知识库进行智能问答，快速获取文档中的信息</Paragraph>
            </Space>
          </Card>

          <Card hoverable onClick={() => navigate('/knowledge-graph')} style={{ cursor: 'pointer' }}>
            <Space direction="vertical" size="middle">
              <FileTextOutlined style={{ fontSize: '48px', color: '#faad14' }} />
              <Title level={4}>知识图谱</Title>
              <Paragraph>将文档中的知识关系可视化，帮助你快速构建结构化认知</Paragraph>
            </Space>
          </Card>
        </div>
      </Space>
    </div>
  )
}

export default Home






