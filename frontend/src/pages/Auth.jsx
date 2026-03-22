import React from 'react'
import { Card, Tabs, Form, Input, Button, Select, message } from 'antd'
import { loginUser, registerUser, resetPassword } from '../api/auth'

import sideImage from '../assets/login-side.png'

const seasonOptions = [
  { value: '春天', label: '春天' },
  { value: '夏天', label: '夏天' },
  { value: '秋天', label: '秋天' },
  { value: '冬天', label: '冬天' },
]

const monthOptions = Array.from({ length: 12 }).map((_, i) => ({
  value: i + 1,
  label: `${i + 1}月`,
}))

const Auth = ({ onAuthed }) => {
  const handleLogin = async (values) => {
    const res = await loginUser(values)
    localStorage.setItem('auth_token', res.token)
    localStorage.setItem('auth_username', res.username)
    message.success('登录成功')
    onAuthed?.(res.username)
  }

  const handleRegister = async (values) => {
    const res = await registerUser(values)
    localStorage.setItem('auth_token', res.token)
    localStorage.setItem('auth_username', res.username)
    message.success('注册并登录成功')
    onAuthed?.(res.username)
  }

  const handleReset = async (values) => {
    await resetPassword(values)
    message.success('密码重置成功，请返回登录页')
  }

  return (
    <div
      style={{
        position: 'relative',
        minHeight: '100vh',
        overflow: 'hidden',
        background: 'transparent',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      {/* 内容层：左右布局 */}
      <div
        style={{
          position: 'relative',
          width: '100%',
          maxWidth: 1200,
          margin: '0 auto',
          padding: '24px 32px',
          // 2fr:1fr 固定左右比例，让左侧“放大两倍”且不会上下换行
          display: 'grid',
          gridTemplateColumns: '2fr 1fr',
          alignItems: 'center',
          justifyItems: 'center',
          columnGap: 'min(48px, 4.5vw)',
        }}
      >
        {/* 左侧：第一张图 */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            overflow: 'hidden',
            borderRadius: 28,
            height: 'clamp(300px, 48vh, 520px)',
          }}
        >
          <img
            src={sideImage}
            alt="LearnMate"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              transform: 'none',
              display: 'block',
            }}
          />
        </div>

        {/* 右侧：登录输入框 */}
        <div
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Card title="LearnMate 本地账户登录" style={{ width: '100%', maxWidth: 390 }}>
            <Tabs
              defaultActiveKey="login"
              items={[
                {
                  key: 'login',
                  label: '登录',
                  children: (
                    <Form layout="vertical" onFinish={handleLogin}>
                      <Form.Item name="username" label="账号" rules={[{ required: true }]}>
                        <Input placeholder="请输入账号" />
                      </Form.Item>
                      <Form.Item name="password" label="密码" rules={[{ required: true }]}>
                        <Input.Password placeholder="请输入密码" />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>登录</Button>
                    </Form>
                  ),
                },
                {
                  key: 'register',
                  label: '注册',
                  children: (
                    <Form layout="vertical" onFinish={handleRegister}>
                      <Form.Item name="username" label="账号" rules={[{ required: true, min: 3 }]}>
                        <Input placeholder="至少 3 位" />
                      </Form.Item>
                      <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
                        <Input.Password placeholder="至少 6 位" />
                      </Form.Item>
                      <Form.Item name="security_q1_season" label="Q1：你最喜欢的季节（X天）" rules={[{ required: true }]}>
                        <Select options={seasonOptions} />
                      </Form.Item>
                      <Form.Item name="security_q2_birth_month" label="Q2：你的生日在几月（X月）" rules={[{ required: true }]}>
                        <Select options={monthOptions} />
                      </Form.Item>
                      <Form.Item name="security_q3_food" label="Q3：你最喜欢的食物" rules={[{ required: true }]}>
                        <Input placeholder="例如：火锅" />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>注册并登录</Button>
                    </Form>
                  ),
                },
                {
                  key: 'reset',
                  label: '找回密码',
                  children: (
                    <Form layout="vertical" onFinish={handleReset}>
                      <Form.Item name="username" label="账号" rules={[{ required: true }]}>
                        <Input placeholder="请输入账号" />
                      </Form.Item>
                      <Form.Item name="security_q1_season" label="Q1：你最喜欢的季节（X天）" rules={[{ required: true }]}>
                        <Select options={seasonOptions} />
                      </Form.Item>
                      <Form.Item name="security_q2_birth_month" label="Q2：你的生日在几月（X月）" rules={[{ required: true }]}>
                        <Select options={monthOptions} />
                      </Form.Item>
                      <Form.Item name="security_q3_food" label="Q3：你最喜欢的食物" rules={[{ required: true }]}>
                        <Input placeholder="例如：火锅" />
                      </Form.Item>
                      <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6 }]}>
                        <Input.Password placeholder="至少 6 位" />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>重置密码</Button>
                    </Form>
                  ),
                },
              ]}
            />
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Auth
