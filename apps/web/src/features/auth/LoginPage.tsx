import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../../services/api'
import { Camera, AlertCircle, Loader } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@hospital.demo')
  const [password, setPassword] = useState('Admin@123456')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const token = await authApi.login(email, password)
      localStorage.setItem('access_token', token.access_token)
      localStorage.setItem('refresh_token', token.refresh_token)
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail
      setError(msg || 'Đăng nhập thất bại. Kiểm tra email và mật khẩu.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0f172a',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          width: 380,
          padding: 32,
          background: '#1e293b',
          borderRadius: 12,
          border: '1px solid #334155',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div
            style={{
              display: 'inline-flex',
              background: '#3b82f6',
              borderRadius: 12,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Camera size={32} color="white" />
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            AI Hospital Camera
          </h1>
          <p style={{ color: '#64748b', marginTop: 4, fontSize: 13 }}>
            Hệ thống giám sát bệnh viện đa kênh & AI
          </p>
        </div>

        <div
          style={{
            background: '#78350f',
            border: '1px solid #b45309',
            borderRadius: 8,
            padding: '10px 14px',
            marginBottom: 20,
            fontSize: 12,
            color: '#fbbf24',
          }}
        >
          ⚠️ <strong>CHẾ ĐỘ DEMO:</strong> Dùng tài khoản mẫu:<br />
          <code>admin@hospital.demo / Admin@123456</code>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              style={inputStyle}
              placeholder="admin@hospital.demo"
            />
          </div>
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: 'block', fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>
              Mật khẩu
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              style={inputStyle}
              placeholder="Nhập mật khẩu"
            />
          </div>

          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#450a0a',
                border: '1px solid #dc2626',
                borderRadius: 8,
                padding: '10px 14px',
                marginBottom: 16,
                fontSize: 13,
                color: '#f87171',
              }}
            >
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px 24px',
              background: '#3b82f6',
              border: 'none',
              borderRadius: 8,
              color: 'white',
              fontWeight: 600,
              fontSize: 14,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
            }}
          >
            {loading ? (
              <>
                <Loader size={16} /> Đang đăng nhập...
              </>
            ) : (
              'Đăng nhập hệ thống'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 14px',
  background: '#0f172a',
  border: '1px solid #334155',
  borderRadius: 8,
  color: '#f8fafc',
  fontSize: 14,
  outline: 'none',
  boxSizing: 'border-box',
}
