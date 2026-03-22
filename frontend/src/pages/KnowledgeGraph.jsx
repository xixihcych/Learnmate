import React, { useEffect, useMemo, useState } from 'react'
import { Button, Card, Col, Divider, List, message, Row, Select, Space, Statistic, Tag, Typography } from 'antd'
import { buildKgFromDocuments, clearKg, extractKgFromDocument, getKgStatistics, getKgTriples, visualizeKg } from '../api/knowledgeGraph'
import { getDocuments } from '../api/document'

const { Title, Paragraph, Text } = Typography

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const KnowledgeGraph = () => {
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({})
  const [triples, setTriples] = useState([])
  const [documents, setDocuments] = useState([])
  const [selectedDocId, setSelectedDocId] = useState(null)
  const [graphUrl, setGraphUrl] = useState('')

  const iframeSrc = useMemo(() => {
    if (!graphUrl) return ''
    if (/^https?:\/\//.test(graphUrl)) return graphUrl
    return `${API_BASE}${graphUrl}`
  }, [graphUrl])

  const refresh = async () => {
    const [s, t, d] = await Promise.all([
      getKgStatistics().catch(() => ({})),
      getKgTriples(120).catch(() => ({ triples: [] })),
      getDocuments().catch(() => []),
    ])
    setStats(s || {})
    setTriples((t && t.triples) || [])
    setDocuments(d || [])
  }

  useEffect(() => {
    refresh()
  }, [])

  const withLoading = async (fn, okMsg) => {
    setLoading(true)
    try {
      const res = await fn()
      if (okMsg) message.success(okMsg)
      await refresh()
      return res
    } catch (e) {
      message.error(e.response?.data?.detail || e.message || '操作失败')
      return null
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Title level={2}>知识图谱</Title>
      <Paragraph type="secondary">
        将文档中的自然语言信息抽取为“实体-关系-实体”结构，并生成可交互的图谱视图。
      </Paragraph>

      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}><Statistic title="节点数" value={stats.nodes_count || 0} /></Col>
          <Col span={6}><Statistic title="关系边数" value={stats.edges_count || 0} /></Col>
          <Col span={6}><Statistic title="三元组数" value={stats.triples_count || 0} /></Col>
          <Col span={6}><Statistic title="实体数" value={stats.entities_count || 0} /></Col>
        </Row>
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            style={{ width: 420 }}
            placeholder="选择一个已处理文档，抽取知识图谱"
            value={selectedDocId}
            onChange={setSelectedDocId}
            options={documents
              .filter((d) => d.status === 'completed')
              .map((d) => ({ value: d.id, label: `${d.id} - ${d.filename}` }))}
          />
          <Button
            type="primary"
            loading={loading}
            onClick={() => withLoading(() => buildKgFromDocuments(), '已从全部已处理文档构建知识图谱')}
          >
            从全部文档构建
          </Button>
          <Button
            loading={loading}
            disabled={!selectedDocId}
            onClick={() => withLoading(() => extractKgFromDocument(selectedDocId), '已从选中文档抽取知识关系')}
          >
            从选中文档抽取
          </Button>
          <Button
            loading={loading}
            onClick={async () => {
              const res = await withLoading(() => visualizeKg(), '已生成图谱可视化')
              if (res?.url) setGraphUrl(res.url)
            }}
          >
            生成思维导图
          </Button>
          <Button
            danger
            loading={loading}
            onClick={async () => {
              const ok = await withLoading(() => clearKg(), '已清空知识图谱')
              if (ok) setGraphUrl('')
            }}
          >
            清空图谱
          </Button>
        </Space>
      </Card>

      <Row gutter={16}>
        <Col span={16}>
          <Card title="图谱可视化（可拖拽/缩放）" style={{ minHeight: 760 }}>
            {iframeSrc ? (
              <iframe
                title="knowledge-graph"
                src={iframeSrc}
                style={{ width: '100%', height: 700, border: '1px solid #eee', borderRadius: 8 }}
              />
            ) : (
              <Paragraph type="secondary">先点击“生成思维导图”，这里会展示自动生成的交互式图谱。</Paragraph>
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="关系三元组（节选）" style={{ minHeight: 760 }}>
            <div style={{ height: 700, overflowY: 'auto', paddingRight: 4 }}>
              <List
                size="small"
                dataSource={triples}
                locale={{ emptyText: '暂无三元组，请先抽取或构建图谱' }}
                renderItem={(t, idx) => (
                  <List.Item key={idx}>
                    <div style={{ lineHeight: 1.5 }}>
                      <Tag color="blue">{t.entity1}</Tag>
                      <Text> — {t.relation} — </Text>
                      <Tag color="green">{t.entity2}</Tag>
                    </div>
                  </List.Item>
                )}
              />
              <Divider />
              <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                说明：这部分是图谱结构化结果，左侧是可视化图谱视图。
              </Paragraph>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default KnowledgeGraph
