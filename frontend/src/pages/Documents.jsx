import React, { useState, useEffect } from 'react'
import { Card, Table, Button, message, Popconfirm, Tag, Space, Typography, Upload, Modal, Tabs, Input } from 'antd'
import { DeleteOutlined, UploadOutlined, ReloadOutlined, PlayCircleOutlined, EyeOutlined } from '@ant-design/icons'
import { getDocuments, deleteDocument, uploadFile, processDocument, getDocument, getDocumentText } from '../api/document'
import dayjs from 'dayjs'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

const Documents = () => {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState({})
  const [detailVisible, setDetailVisible] = useState(false)
  const [currentDocument, setCurrentDocument] = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewText, setPreviewText] = useState('')

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const data = await getDocuments()
      setDocuments(data)
    } catch (error) {
      message.error('获取文档列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleDelete = async (documentId) => {
    try {
      await deleteDocument(documentId)
      message.success('删除成功')
      fetchDocuments()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleProcess = async (documentId) => {
    setProcessing({ ...processing, [documentId]: true })
    try {
      const result = await processDocument(documentId)
      message.success(`文档处理成功！生成了 ${result.chunk_count} 个文本块`)
      fetchDocuments()
    } catch (error) {
      message.error(`处理失败: ${error.response?.data?.detail || error.message}`)
    } finally {
      setProcessing({ ...processing, [documentId]: false })
    }
  }

  const handleViewDetail = async (documentId) => {
    try {
      const doc = await getDocument(documentId)
      setCurrentDocument(doc)
      setDetailVisible(true)
      setPreviewText('')
    } catch (error) {
      message.error('获取文档详情失败')
    }
  }

  const handleUpload = async (file) => {
    setUploading(true)
    try {
      const result = await uploadFile(file)
      message.success(result?.message || `文件 ${file.name} 上传成功！`)
      fetchDocuments()
    } catch (error) {
      message.error(`上传失败: ${error.response?.data?.detail || error.message}`)
    } finally {
      setUploading(false)
    }
    return false
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '-'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      width: 520,
      ellipsis: true,
      render: (text, record) => (
        <Button type="link" onClick={() => handleViewDetail(record.id)} style={{ padding: 0 }}>
          <Text ellipsis={{ tooltip: text }} style={{ maxWidth: 480, display: 'inline-block' }}>
            {text}
          </Text>
        </Button>
      ),
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (type) => <Tag color="blue">{type.toUpperCase()}</Tag>,
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size) => formatFileSize(size),
    },
    {
      title: '页数',
      dataIndex: 'page_count',
      key: 'page_count',
      render: (count) => count || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          uploaded: { color: 'blue', text: '已上传' },
          processing: { color: 'orange', text: '处理中' },
          completed: { color: 'green', text: '已完成' },
          failed: { color: 'red', text: '失败' },
        }
        const s = statusMap[status] || { color: 'default', text: status }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            size="small"
            onClick={() => handleProcess(record.id)}
            loading={processing[record.id]}
            disabled={record.status === 'completed' || record.status === 'processing'}
          >
            {record.status === 'completed' ? '已处理' : '处理'}
          </Button>
          <Popconfirm
            title="确定要删除这个文档吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button danger icon={<DeleteOutlined />} size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: '20px', width: '100%', justifyContent: 'space-between' }}>
        <Title level={2}>文档管理</Title>
        <Space>
          <Upload
            accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.bmp,.webp,.tiff,.tif,.gif"
            beforeUpload={handleUpload}
            showUploadList={false}
          >
            <Button type="primary" icon={<UploadOutlined />} loading={uploading}>
              上传文档/图片
            </Button>
          </Upload>
          <Button icon={<ReloadOutlined />} onClick={fetchDocuments}>
            刷新
          </Button>
        </Space>
      </Space>

      <Card>
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          scroll={{ x: 900 }}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 文档详情Modal */}
      <Modal
        title="文档详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {currentDocument && (
          <Tabs
            defaultActiveKey="meta"
            items={[
              {
                key: 'meta',
                label: '信息',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }} size="middle">
                    <div>
                      <Text strong>文件名：</Text>
                      <Text>{currentDocument.filename}</Text>
                    </div>
                    <div>
                      <Text strong>类型：</Text>
                      <Tag color="blue">{currentDocument.file_type.toUpperCase()}</Tag>
                    </div>
                    <div>
                      <Text strong>大小：</Text>
                      <Text>{formatFileSize(currentDocument.file_size)}</Text>
                    </div>
                    <div>
                      <Text strong>页数：</Text>
                      <Text>{currentDocument.page_count || '-'}</Text>
                    </div>
                    <div>
                      <Text strong>状态：</Text>
                      <Tag
                        color={
                          currentDocument.status === 'completed'
                            ? 'green'
                            : currentDocument.status === 'processing'
                              ? 'orange'
                              : currentDocument.status === 'failed'
                                ? 'red'
                                : 'blue'
                        }
                      >
                        {currentDocument.status === 'completed'
                          ? '已完成'
                          : currentDocument.status === 'processing'
                            ? '处理中'
                            : currentDocument.status === 'failed'
                              ? '失败'
                              : '已上传'}
                      </Tag>
                    </div>
                    <div>
                      <Text strong>上传时间：</Text>
                      <Text>{dayjs(currentDocument.upload_time).format('YYYY-MM-DD HH:mm:ss')}</Text>
                    </div>
                    <div>
                      <Text strong>文件路径：</Text>
                      <Text code>{currentDocument.file_path}</Text>
                    </div>
                    {currentDocument.status !== 'completed' && (
                      <Button
                        type="primary"
                        icon={<PlayCircleOutlined />}
                        onClick={() => {
                          handleProcess(currentDocument.id)
                          setDetailVisible(false)
                        }}
                        loading={processing[currentDocument.id]}
                      >
                        处理文档
                      </Button>
                    )}
                  </Space>
                ),
              },
              {
                key: 'preview',
                label: '文本预览（可复制）',
                children: (
                  <div>
                    <Space style={{ marginBottom: 12 }}>
                      <Button
                        icon={<EyeOutlined />}
                        loading={previewLoading}
                        onClick={async () => {
                          setPreviewLoading(true)
                          try {
                            const res = await getDocumentText(currentDocument.id)
                            setPreviewText(res.text || '')
                          } catch (e) {
                            message.error(e.response?.data?.detail || '获取预览文本失败')
                          } finally {
                            setPreviewLoading(false)
                          }
                        }}
                      >
                        加载预览文本
                      </Button>
                      <Button
                        disabled={!previewText}
                        onClick={() => {
                          navigator.clipboard.writeText(previewText || '')
                          message.success('已复制全文')
                        }}
                      >
                        复制全文
                      </Button>
                    </Space>

                    <TextArea
                      value={previewText}
                      readOnly
                      placeholder="点击“加载预览文本”后即可在此处选词复制。"
                      style={{ height: 420, fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }}
                    />
                    <Paragraph type="secondary" style={{ marginTop: 8 }}>
                      提示：这里展示的是解析出的纯文本，支持选词复制；PDF 原格式预览后续也可以再加。
                    </Paragraph>
                  </div>
                ),
              },
            ]}
          />
        )}
      </Modal>
    </div>
  )
}

export default Documents

