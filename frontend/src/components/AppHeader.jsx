import React from 'react'
import { Layout, Menu, Button, Space, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import { FileTextOutlined, MessageOutlined, HomeOutlined, ApartmentOutlined } from '@ant-design/icons'

const { Header } = Layout

const { Text } = Typography

const AppHeader = ({ username, onLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/documents',
      icon: <FileTextOutlined />,
      label: '文档管理',
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: 'AI问答',
    },
    {
      key: '/knowledge-graph',
      icon: <ApartmentOutlined />,
      label: '知识图谱',
    },
  ]

  return (
    <Header style={{ background: '#fff', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        <div style={{ fontSize: '20px', fontWeight: 'bold', marginRight: '40px', color: '#1890ff' }}>
          LearnMate
        </div>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, borderBottom: 'none' }}
        />
        <Space>
          <Text type="secondary">{username}</Text>
          <Button onClick={onLogout}>退出登录</Button>
        </Space>
      </div>
    </Header>
  )
}

export default AppHeader






