import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { camerasApi } from '../../services/api'
import type { Camera, CameraStatus, CameraProtocol } from '../../types'
import {
  Plus,
  Search,
  TestTube2,
  Loader,
  RefreshCw,
  AlertCircle,
  Video,
  X,
  CheckCircle2,
  Edit2,
  Trash2,
} from 'lucide-react'

const STATUS_COLORS: Record<CameraStatus, string> = {
  online: '#22c55e',
  offline: '#ef4444',
  error: '#f97316',
  disabled: '#6b7280',
  unknown: '#94a3b8',
}

const STATUS_LABELS: Record<CameraStatus, string> = {
  online: 'Trực tuyến',
  offline: 'Ngoại tuyến',
  error: 'Lỗi',
  disabled: 'Đã tắt',
  unknown: 'Chưa rõ',
}

export default function CamerasPage() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; error?: string; latency_ms?: number }>>({})
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['cameras', { page, search }],
    queryFn: () => camerasApi.list({ page, page_size: 20, search: search || undefined }),
  })

  const testMutation = useMutation({
    mutationFn: (id: string) => camerasApi.testConnection(id),
    onMutate: (id) => setTestingId(id),
    onSuccess: (result: any, id: string) => {
      setTestResults((prev) => ({ ...prev, [id]: result }))
      qc.invalidateQueries({ queryKey: ['cameras'] })
    },
    onError: (_err, id) => {
      setTestResults((prev) => ({ ...prev, [id]: { success: false, error: 'Kiểm tra thất bại' } }))
    },
    onSettled: () => setTestingId(null),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => camerasApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cameras'] }),
  })

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Video size={24} color="#3b82f6" />
            Quản lý Danh mục Camera
          </h1>
          <p style={{ color: '#64748b', marginTop: 4, fontSize: 13 }}>
            Danh sách thiết bị IP Camera & Kênh NVR ({data?.total || 0} thiết bị)
          </p>
        </div>

        <button
          onClick={() => {
            setEditingCamera(null)
            setIsModalOpen(true)
          }}
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
          <Plus size={16} /> Thêm Camera Mới
        </button>
      </div>

      {/* Search Bar */}
      <div style={{ position: 'relative', marginBottom: 20 }}>
        <Search
          size={16}
          style={{
            position: 'absolute',
            left: 12,
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#64748b',
          }}
        />
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setPage(1)
          }}
          placeholder="Tìm theo tên camera, địa chỉ IP..."
          style={{
            padding: '10px 14px 10px 38px',
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 8,
            color: '#f8fafc',
            fontSize: 13,
            outline: 'none',
            width: '100%',
            maxWidth: 360,
          }}
        />
      </div>

      {/* Table */}
      {isLoading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Đang tải danh sách camera...</div>
      ) : isError ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#ef4444' }}>
          <AlertCircle size={32} />
          <p>Không thể tải dữ liệu camera</p>
          <button onClick={() => refetch()} style={{ marginTop: 8, padding: '6px 12px', background: '#334155', color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
            <RefreshCw size={12} /> Thử lại
          </button>
        </div>
      ) : (
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#0f172a' }}>
                {['Tên camera', 'Địa chỉ IP', 'Giao thức', 'Trạng thái', 'Phân tích AI', 'Chế độ', 'Thao tác'].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: '12px 16px',
                      textAlign: 'left',
                      fontSize: 12,
                      color: '#64748b',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(data?.items || []).map((cam) => (
                <CameraRow
                  key={cam.id}
                  camera={cam}
                  testing={testingId === cam.id}
                  testResult={testResults[cam.id]}
                  onTest={() => testMutation.mutate(cam.id)}
                  onEdit={() => {
                    setEditingCamera(cam)
                    setIsModalOpen(true)
                  }}
                  onDelete={() => {
                    if (confirm(`Bạn có chắc muốn xóa camera "${cam.name}" khỏi hệ thống?`)) {
                      deleteMutation.mutate(cam.id)
                    }
                  }}
                />
              ))}
              {(data?.items || []).length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
                    Không có camera nào phù hợp
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal Thêm / Sửa Camera */}
      {isModalOpen && (
        <CameraFormModal
          initialCamera={editingCamera}
          onClose={() => {
            setIsModalOpen(false)
            setEditingCamera(null)
          }}
          onSuccess={() => {
            setIsModalOpen(false)
            setEditingCamera(null)
            qc.invalidateQueries({ queryKey: ['cameras'] })
          }}
        />
      )}
    </div>
  )
}

function CameraRow({
  camera,
  testing,
  testResult,
  onTest,
  onEdit,
  onDelete,
}: {
  camera: Camera
  testing: boolean
  testResult?: { success: boolean; error?: string; latency_ms?: number }
  onTest: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  return (
    <tr style={{ borderTop: '1px solid #334155' }}>
      <td style={{ padding: '12px 16px' }}>
        <div style={{ fontSize: 13, color: '#f8fafc', fontWeight: 600 }}>{camera.name}</div>
        {camera.manufacturer && (
          <div style={{ fontSize: 11, color: '#64748b' }}>{camera.manufacturer}</div>
        )}
      </td>
      <td style={{ padding: '12px 16px', fontSize: 13, color: '#94a3b8' }}>
        {camera.ip_address || '—'}
      </td>
      <td style={{ padding: '12px 16px', fontSize: 12, color: '#94a3b8', textTransform: 'uppercase' }}>
        {camera.protocol}
      </td>
      <td style={{ padding: '12px 16px' }}>
        <span
          style={{
            padding: '3px 10px',
            borderRadius: 20,
            fontSize: 11,
            fontWeight: 600,
            background: `${STATUS_COLORS[camera.status] || '#94a3b8'}22`,
            color: STATUS_COLORS[camera.status] || '#94a3b8',
          }}
        >
          {STATUS_LABELS[camera.status] || camera.status}
        </span>
      </td>
      <td style={{ padding: '12px 16px', fontSize: 13 }}>
        <span style={{ color: camera.ai_enabled ? '#22c55e' : '#64748b', fontWeight: 500 }}>
          {camera.ai_enabled ? 'Đang bật' : 'Tắt'}
        </span>
      </td>
      <td style={{ padding: '12px 16px' }}>
        {camera.is_demo ? (
          <span
            style={{
              padding: '2px 8px',
              borderRadius: 12,
              fontSize: 10,
              background: '#78350f33',
              color: '#fbbf24',
              border: '1px solid #b45309',
            }}
          >
            DEMO
          </span>
        ) : (
          <span style={{ fontSize: 11, color: '#34d399', fontWeight: 600 }}>Vật lý</span>
        )}
      </td>
      <td style={{ padding: '12px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={onTest}
            disabled={testing}
            title="Kiểm tra kết nối và độ trễ"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '5px 8px',
              background: '#334155',
              border: 'none',
              borderRadius: 6,
              color: '#f8fafc',
              fontSize: 11,
              cursor: testing ? 'not-allowed' : 'pointer',
            }}
          >
            {testing ? <Loader size={12} className="animate-spin" /> : <TestTube2 size={12} />} Kiểm tra
          </button>

          <button
            onClick={onEdit}
            title="Chỉnh sửa camera"
            style={{
              background: '#0284c722',
              border: '1px solid #0284c7',
              borderRadius: 6,
              color: '#38bdf8',
              padding: '5px 8px',
              fontSize: 11,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Edit2 size={12} /> Sửa
          </button>

          <button
            onClick={onDelete}
            title="Xóa camera"
            style={{
              background: '#7f1d1d22',
              border: '1px solid #dc2626',
              borderRadius: 6,
              color: '#f87171',
              padding: '5px 8px',
              fontSize: 11,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <Trash2 size={12} /> Xóa
          </button>

          {testResult && (
            <span style={{ fontSize: 11, color: testResult.success ? '#22c55e' : '#ef4444', marginLeft: 4 }}>
              {testResult.success
                ? `✓ (${testResult.latency_ms?.toFixed(0)}ms)`
                : `✗ Lỗi`}
            </span>
          )}
        </div>
      </td>
    </tr>
  )
}

function CameraFormModal({
  initialCamera,
  onClose,
  onSuccess,
}: {
  initialCamera?: Camera | null
  onClose: () => void
  onSuccess: () => void
}) {
  const isEdit = !!initialCamera
  const [name, setName] = useState(initialCamera?.name || '')
  const [manufacturer, setManufacturer] = useState(initialCamera?.manufacturer || 'Dahua')
  const [model, setModel] = useState(initialCamera?.model || '')
  const [ipAddress, setIpAddress] = useState(initialCamera?.ip_address || '')
  const [port, setPort] = useState(initialCamera?.port || 554)
  const [protocol, setProtocol] = useState<CameraProtocol>(initialCamera?.protocol || 'rtsp')
  const [rtspUrl, setRtspUrl] = useState('')
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [aiEnabled, setAiEnabled] = useState(initialCamera ? initialCamera.ai_enabled : true)
  const [isDemo, setIsDemo] = useState(initialCamera ? initialCamera.is_demo : false)
  const [tags, setTags] = useState(initialCamera?.tags?.join(', ') || 'sanh, vat-ly')

  const [saving, setSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      setErrorMsg('Vui lòng nhập tên nhận diện camera')
      return
    }

    setSaving(true)
    setErrorMsg(null)

    try {
      const tagList = tags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)

      const payload: Record<string, any> = {
        name: name.trim(),
        manufacturer: manufacturer || undefined,
        model: model.trim() || undefined,
        ip_address: ipAddress.trim() || undefined,
        port: port ? Number(port) : 554,
        protocol,
        ai_enabled: aiEnabled,
        is_demo: isDemo,
        tags: tagList,
      }

      if (username.trim()) payload.username = username.trim()
      if (password) payload.password = password
      if (rtspUrl.trim()) payload.rtsp_main_url = rtspUrl.trim()

      if (isEdit && initialCamera) {
        await camerasApi.update(initialCamera.id, payload)
      } else {
        await camerasApi.create(payload)
      }

      onSuccess()
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Không thể lưu camera')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)',
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
          maxWidth: 600,
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #334155',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#0f172a',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Video size={20} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: '#f8fafc' }}>
              {isEdit ? `Chỉnh Sửa Camera: ${initialCamera?.name}` : 'Thêm Thiết bị Camera Mới'}
            </h3>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: 4,
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} style={{ padding: 20 }}>
          {errorMsg && (
            <div
              style={{
                marginBottom: 16,
                padding: '10px 12px',
                background: '#7f1d1d33',
                border: '1px solid #dc2626',
                borderRadius: 6,
                fontSize: 13,
                color: '#f87171',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Tên Camera <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="text"
                placeholder="Ví dụ: Camera Dahua Sảnh Cấp Cứu, Camera Phòng Mổ 02..."
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Hãng sản xuất
              </label>
              <select
                value={manufacturer}
                onChange={(e) => setManufacturer(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              >
                <option value="Dahua">Dahua</option>
                <option value="Hikvision">Hikvision</option>
                <option value="Uniview">Uniview (UNV)</option>
                <option value="Tiandy">Tiandy</option>
                <option value="Axis">Axis Communications</option>
                <option value="Hanwha">Hanwha Vision</option>
                <option value="Other">Khác (ONVIF Standard)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Giao thức kết nối
              </label>
              <select
                value={protocol}
                onChange={(e) => setProtocol(e.target.value as CameraProtocol)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              >
                <option value="rtsp">RTSP (Real Time Streaming)</option>
                <option value="onvif">ONVIF Profile S/T</option>
                <option value="http">HTTP / HLS Web Stream</option>
                <option value="mock">MOCK (Mô phỏng thử nghiệm)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Địa chỉ IP Camera / NVR
              </label>
              <input
                type="text"
                placeholder="Ví dụ: 192.168.111.168"
                value={ipAddress}
                onChange={(e) => setIpAddress(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Cổng dịch vụ (Port)
              </label>
              <input
                type="number"
                value={port}
                onChange={(e) => setPort(Number(e.target.value))}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                URL Luồng RTSP (Main Stream) {isEdit && '(để trống nếu không đổi)'}
              </label>
              <input
                type="text"
                placeholder="rtsp://admin:L2622B4F@192.168.111.168:554/cam/realmonitor?channel=1&subtype=0"
                value={rtspUrl}
                onChange={(e) => setRtspUrl(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Tài khoản Camera (Username)
              </label>
              <input
                type="text"
                placeholder="admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Mật khẩu Camera {isEdit && '(để trống nếu không đổi)'}
              </label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div style={{ gridColumn: 'span 2' }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Nhãn phân nhóm (Tags, cách nhau bằng dấu phẩy)
              </label>
              <input
                type="text"
                placeholder="cap-cuu, phong-mo, ngoai-canh, tang-1"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>
          </div>

          {/* Tùy chọn AI */}
          <div style={{ borderTop: '1px solid #334155', paddingTop: 14, marginBottom: 18, display: 'flex', gap: 24 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#f8fafc', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={aiEnabled}
                onChange={(e) => setAiEnabled(e.target.checked)}
                style={{ accentColor: '#2563eb', width: 16, height: 16 }}
              />
              Kích hoạt Phân tích AI Computer Vision
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: '#f8fafc', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isDemo}
                onChange={(e) => setIsDemo(e.target.checked)}
                style={{ accentColor: '#f59e0b', width: 16, height: 16 }}
              />
              Chế độ Demo (Mô phỏng)
            </label>
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              style={{
                background: '#334155',
                color: '#cbd5e1',
                border: 'none',
                borderRadius: 6,
                padding: '9px 16px',
                fontSize: 13,
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={saving}
              style={{
                background: saving ? '#475569' : '#2563eb',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                padding: '9px 18px',
                fontSize: 13,
                fontWeight: 600,
                cursor: saving ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              {saving ? <Loader size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
              {isEdit ? 'Cập Nhật Thay Đổi' : 'Lưu & Kết Nối'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
