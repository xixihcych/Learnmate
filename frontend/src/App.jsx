import React, { useMemo, useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppHeader from './components/AppHeader'
import Home from './pages/Home'
import Documents from './pages/Documents'
import Chat from './pages/Chat'
import Auth from './pages/Auth'
import KnowledgeGraph from './pages/KnowledgeGraph'
import './App.css'
import homeBg from './assets/home-bg.png'

const { Content } = Layout

function App() {
  const [username, setUsername] = useState(localStorage.getItem('auth_username') || '')
  const isAuthed = useMemo(() => Boolean(localStorage.getItem('auth_token')), [username])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_username')
    setUsername('')
  }

  const content = !isAuthed ? (
    <Auth onAuthed={setUsername} />
  ) : (
    <Router>
      <Layout className="app-layout" style={{ background: 'transparent' }}>
        <AppHeader username={username} onLogout={handleLogout} />
        <Content className="app-content" style={{ background: 'transparent' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  )

  return (
    <div style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden' }}>
      {/* 全局背景层：把“第一张图”用作统一背景 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url(${homeBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          opacity: 0.9,
          zIndex: 0,
        }}
      />
      <div style={{ position: 'relative', zIndex: 1 }}>{content}</div>
    </div>
  )
}

export default App






