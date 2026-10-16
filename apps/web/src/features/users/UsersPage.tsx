import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../../services/api'
import {
  Users,
  Plus,
  Shield,
  Trash2,
  CheckCircle2,
  XCircle,
  Loader,
  AlertCircle,
  X,
  Mail,
  UserCheck,
} from 'lucide-react'

export default function UsersPage() {
  const qc = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isAddUserOpen, setIsAddUserOpen] = useState(false)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['users', { page, search }],
    queryFn: () => usersApi.list({ page, page_size: 20, search: search || undefined }),
  })

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      usersApi.update(id, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => usersApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }),
  })

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Users size={24} color="#3b82f6" />
            Quản trị Người dùng & Phân quyền (RBAC)
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            Quản lý tài khoản truy cập hệ thống camera và phân quyền vận hành ({data?.total || 0} tài khoản)
          </p>
        </div>

        <button
          onClick={() => setIsAddUserOpen(true)}
          style={{
            background: '#2563eb',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '10px 18px',
            fontSize: 13,
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            boxShadow: '0 2px 8px rgba(37,99,235,0.3)',
          }}
        >
          <Plus size={16} /> Thêm Người Dùng
        </button>
      </div>

      {/* User Table */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#0f172a' }}>
              {['Họ và tên', 'Email tài khoản', 'Điện thoại', 'Quyền Quản Trị', 'Trạng thái', 'Hành động'].map((h) => (
                <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, color: '#64748b', textTransform: 'uppercase' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} style={{ padding: 30, textAlign: 'center', color: '#64748b' }}>
                  Đang tải danh sách người dùng...
                </td>
              </tr>
            ) : (data?.items || []).map((u) => (
              <tr key={u.id} style={{ borderTop: '1px solid #334155' }}>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#f8fafc', fontWeight: 600 }}>
                  {u.full_name}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#94a3b8' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Mail size={13} color="#64748b" /> {u.email}
                  </div>
                </td>
                <td style={{ padding: '12px 16px', fontSize: 13, color: '#94a3b8' }}>
                  {u.phone || '—'}
                </td>
                <td style={{ padding: '12px 16px', fontSize: 12 }}>
                  <span
                    style={{
                      padding: '3px 8px',
                      borderRadius: 6,
                      background: u.is_superuser ? '#78350f33' : '#3b82f622',
                      color: u.is_superuser ? '#fbbf24' : '#38bdf8',
                      fontWeight: 600,
                    }}
                  >
                    {u.is_superuser ? 'Super Administrator' : 'Operator / Nhân viên'}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontSize: 12 }}>
                  <button
                    onClick={() => toggleActiveMutation.mutate({ id: u.id, is_active: !u.is_active })}
                    style={{
                      background: u.is_active ? '#064e3b33' : '#7f1d1d33',
                      border: `1px solid ${u.is_active ? '#059669' : '#dc2626'}`,
                      color: u.is_active ? '#34d399' : '#f87171',
                      borderRadius: 14,
                      padding: '2px 10px',
                      cursor: 'pointer',
                      fontSize: 11,
                      fontWeight: 600,
                    }}
                  >
                    {u.is_active ? '✓ Đang hoạt động' : '✗ Đã khóa'}
                  </button>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <button
                    onClick={() => {
                      if (confirm(`Bạn có chắc muốn xóa tài khoản ${u.full_name} (${u.email})?`)) {
                        deleteMutation.mutate(u.id)
                      }
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: 4,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                      fontSize: 12,
                    }}
                  >
                    <Trash2 size={14} /> Xóa
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add User Modal */}
      {isAddUserOpen && (
        <AddUserModal
          onClose={() => setIsAddUserOpen(false)}
          onSuccess={() => {
            setIsAddUserOpen(false)
            qc.invalidateQueries({ queryKey: ['users'] })
          }}
        />
      )}
    </div>
  )
}

function AddUserModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [role, setRole] = useState('Operator')
  const [isSuperuser, setIsSuperuser] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fullName.trim() || !email.trim() || !password) {
      setError('Vui lòng điền đầy đủ họ tên, email và mật khẩu')
      return
    }

    setSaving(true)
    setError(null)
    try {
      await usersApi.create(
        {
          full_name: fullName.trim(),
          email: email.trim(),
          password,
          phone: phone.trim() || undefined,
          is_superuser: isSuperuser,
        },
        role
      )
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi tạo tài khoản')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0,0,0,0.7)',
        backdropFilter: 'blur(3px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: 16,
      }}
    >
      <div
        style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: 12,
          width: '100%',
          maxWidth: 480,
          boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            padding: '16px 20px',
            background: '#0f172a',
            borderBottom: '1px solid #334155',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <UserCheck size={18} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: '#f8fafc' }}>
              Thêm Tài Khoản Người Dùng Mới
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: 20 }}>
          {error && (
            <div
              style={{
                marginBottom: 14,
                padding: '8px 12px',
                background: '#7f1d1d33',
                border: '1px solid #dc2626',
                borderRadius: 6,
                color: '#f87171',
                fontSize: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <AlertCircle size={14} />
              <span>{error}</span>
            </div>
          )}

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
              Họ và Tên Nhân Viên *
            </label>
            <input
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Nguyễn Văn A"
              style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
              Email Đăng Nhập *
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="bs.nguyenvana@hospital.vn"
              style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
              Mật Khẩu Khởi Tạo *
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={inputStyle}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 14 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Số Điện Thoại
              </label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="0912345678" style={inputStyle} />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Vai Trò
              </label>
              <select value={role} onChange={(e) => setRole(e.target.value)} style={inputStyle}>
                <option value="Operator">Operator (Vận hành)</option>
                <option value="Viewer">Viewer (Chỉ xem)</option>
                <option value="Administrator">Administrator (Quản trị)</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: 18 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#f8fafc', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isSuperuser}
                onChange={(e) => setIsSuperuser(e.target.checked)}
                style={{ accentColor: '#2563eb', width: 15, height: 15 }}
              />
              Cấp quyền Toàn quyền Quản trị (Superuser)
            </label>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
            <button type="button" onClick={onClose} style={btnCancelStyle}>
              Hủy
            </button>
            <button type="submit" disabled={saving} style={btnSubmitStyle}>
              {saving ? <Loader size={14} className="animate-spin" /> : <CheckCircle2 size={14} />} Tạo Tài Khoản
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  background: '#0f172a',
  border: '1px solid #334155',
  borderRadius: 6,
  padding: '8px 12px',
  color: '#f8fafc',
  fontSize: 13,
  outline: 'none',
}

const btnCancelStyle: React.CSSProperties = {
  background: '#334155',
  color: '#cbd5e1',
  border: 'none',
  borderRadius: 6,
  padding: '8px 14px',
  fontSize: 13,
  cursor: 'pointer',
}

const btnSubmitStyle: React.CSSProperties = {
  background: '#2563eb',
  color: '#fff',
  border: 'none',
  borderRadius: 6,
  padding: '8px 16px',
  fontSize: 13,
  fontWeight: 600,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: 6,
}
