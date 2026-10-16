import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { departmentsApi } from '../../services/api'
import {
  Building2,
  Plus,
  MapPin,
  Trash2,
  Edit2,
  Loader,
  AlertCircle,
  X,
  CheckCircle2,
} from 'lucide-react'

export default function DepartmentsPage() {
  const qc = useQueryClient()
  const [selectedDeptId, setSelectedDeptId] = useState<string | null>(null)
  const [isAddDeptOpen, setIsAddDeptOpen] = useState(false)
  const [isAddLocOpen, setIsAddLocOpen] = useState(false)
  const [editingDept, setEditingDept] = useState<any | null>(null)

  // Queries
  const { data: departments, isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: departmentsApi.list,
  })

  const { data: locations, isLoading: locLoading } = useQuery({
    queryKey: ['locations', selectedDeptId],
    queryFn: () => (selectedDeptId ? departmentsApi.locations(selectedDeptId) : Promise.resolve([])),
    enabled: !!selectedDeptId,
  })

  // Set first department selected by default
  React.useEffect(() => {
    if (departments && departments.length > 0 && !selectedDeptId) {
      setSelectedDeptId(departments[0].id)
    }
  }, [departments, selectedDeptId])

  const deleteDeptMutation = useMutation({
    mutationFn: (id: string) => departmentsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['departments'] })
      setSelectedDeptId(null)
    },
  })

  const deleteLocMutation = useMutation({
    mutationFn: (id: string) => departmentsApi.deleteLocation(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['locations', selectedDeptId] })
    },
  })

  const selectedDept = departments?.find((d) => d.id === selectedDeptId)

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#f8fafc', margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Building2 size={26} color="#3b82f6" />
            Quản lý Khoa Phòng & Khu Vực Giám Sát
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            Cấu trúc phân cấp sơ đồ bệnh viện phục vụ gán camera và phân quyền sự cố
          </p>
        </div>

        <button
          onClick={() => setIsAddDeptOpen(true)}
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
          <Plus size={16} /> Thêm Khoa Phòng
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20 }}>
        {/* Danh sách Khoa Phòng */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12, overflow: 'hidden' }}>
          <div style={{ padding: '14px 18px', background: '#0f172a', borderBottom: '1px solid #334155', fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>
            Khoa Phòng ({departments?.length || 0})
          </div>

          {isLoading ? (
            <div style={{ padding: 30, textAlign: 'center', color: '#64748b' }}>Đang tải danh sách khoa phòng...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {(departments || []).map((dept) => {
                const isSelected = dept.id === selectedDeptId
                return (
                  <div
                    key={dept.id}
                    onClick={() => setSelectedDeptId(dept.id)}
                    style={{
                      padding: '12px 16px',
                      borderBottom: '1px solid #334155',
                      background: isSelected ? '#334155' : 'transparent',
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      transition: 'background 0.15s',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: isSelected ? '#38bdf8' : '#f8fafc' }}>
                        {dept.name}
                      </div>
                      {dept.code && (
                        <span style={{ fontSize: 11, color: '#94a3b8', background: '#0f172a', padding: '1px 6px', borderRadius: 4, marginTop: 4, display: 'inline-block' }}>
                          Mã: {dept.code}
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setEditingDept(dept)
                        }}
                        title="Chỉnh sửa khoa phòng"
                        style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: 4 }}
                      >
                        <Edit2 size={14} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if (confirm(`Bạn có chắc muốn xóa khoa phòng "${dept.name}"?`)) {
                            deleteDeptMutation.mutate(dept.id)
                          }
                        }}
                        title="Xóa khoa phòng"
                        style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: 4 }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Danh sách Khu Vực trực thuộc Khoa Phòng được chọn */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div
            style={{
              padding: '14px 20px',
              background: '#0f172a',
              borderBottom: '1px solid #334155',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div style={{ fontSize: 15, fontWeight: 600, color: '#f8fafc' }}>
                Khu Vực & Phòng Trực Thuộc: {selectedDept?.name || 'Chưa chọn'}
              </div>
              <div style={{ fontSize: 12, color: '#64748b' }}>
                {selectedDept?.description || 'Khu vực gắn camera an ninh'}
              </div>
            </div>

            {selectedDeptId && (
              <button
                onClick={() => setIsAddLocOpen(true)}
                style={{
                  background: '#0284c7',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  padding: '7px 14px',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                }}
              >
                <Plus size={14} /> Thêm Khu Vực
              </button>
            )}
          </div>

          <div style={{ padding: 20, flex: 1 }}>
            {!selectedDeptId ? (
              <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Vui lòng chọn một khoa phòng bên trái</div>
            ) : locLoading ? (
              <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Đang tải khu vực...</div>
            ) : (locations || []).length === 0 ? (
              <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
                Khoa phòng này chưa có khu vực cụ thể. Hãy bấm "Thêm Khu Vực" để tạo phòng mổ, sảnh, hành lang...
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
                {locations?.map((loc: any) => (
                  <div
                    key={loc.id}
                    style={{
                      background: '#0f172a',
                      border: '1px solid #334155',
                      borderRadius: 8,
                      padding: 14,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                        <MapPin size={16} color="#38bdf8" />
                        <span style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>{loc.name}</span>
                      </div>
                      <div style={{ fontSize: 12, color: '#94a3b8' }}>
                        Tòa: {loc.building || '—'} | Tầng: {loc.floor || '—'} | Phòng: {loc.room || '—'}
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
                      <button
                        onClick={() => {
                          if (confirm(`Bạn có chắc muốn xóa khu vực "${loc.name}"?`)) {
                            deleteLocMutation.mutate(loc.id)
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
                        <Trash2 size={13} /> Xóa
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal Thêm Khoa Phòng */}
      {isAddDeptOpen && (
        <DeptModal
          title="Thêm Khoa Phòng Mới"
          onClose={() => setIsAddDeptOpen(false)}
          onSubmit={async (data) => {
            await departmentsApi.create(data)
            qc.invalidateQueries({ queryKey: ['departments'] })
            setIsAddDeptOpen(false)
          }}
        />
      )}

      {/* Modal Sửa Khoa Phòng */}
      {editingDept && (
        <DeptModal
          title={`Sửa Khoa Phòng: ${editingDept.name}`}
          initialData={editingDept}
          onClose={() => setEditingDept(null)}
          onSubmit={async (data) => {
            await departmentsApi.update(editingDept.id, data)
            qc.invalidateQueries({ queryKey: ['departments'] })
            setEditingDept(null)
          }}
        />
      )}

      {/* Modal Thêm Khu Vực */}
      {isAddLocOpen && selectedDeptId && (
        <LocationModal
          deptId={selectedDeptId}
          onClose={() => setIsAddLocOpen(false)}
          onSubmit={async (data) => {
            await departmentsApi.createLocation(data)
            qc.invalidateQueries({ queryKey: ['locations', selectedDeptId] })
            setIsAddLocOpen(false)
          }}
        />
      )}
    </div>
  )
}

function DeptModal({
  title,
  initialData,
  onClose,
  onSubmit,
}: {
  title: string
  initialData?: any
  onClose: () => void
  onSubmit: (data: any) => Promise<void>
}) {
  const [name, setName] = useState(initialData?.name || '')
  const [code, setCode] = useState(initialData?.code || '')
  const [desc, setDesc] = useState(initialData?.description || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    setError(null)
    try {
      await onSubmit({ name: name.trim(), code: code.trim() || undefined, description: desc.trim() || undefined })
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi lưu thông tin')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ModalWrapper title={title} onClose={onClose}>
      <form onSubmit={handleSubmit} style={{ padding: 20 }}>
        {error && <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 12 }}>{error}</div>}
        <div style={{ marginBottom: 14 }}>
          <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Tên Khoa Phòng *</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Khoa Cấp Cứu, Khoa Phẫu Thuật..."
            style={inputStyle}
          />
        </div>
        <div style={{ marginBottom: 14 }}>
          <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Mã Viết Tắt</label>
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="ER, OT, ICU..." style={inputStyle} />
        </div>
        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Mô Tả</label>
          <textarea value={desc} onChange={(e) => setDesc(e.target.value)} rows={3} style={inputStyle} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
          <button type="button" onClick={onClose} style={btnCancelStyle}>
            Hủy
          </button>
          <button type="submit" disabled={saving} style={btnSubmitStyle}>
            {saving ? <Loader size={14} className="animate-spin" /> : <CheckCircle2 size={14} />} Lưu
          </button>
        </div>
      </form>
    </ModalWrapper>
  )
}

function LocationModal({
  deptId,
  onClose,
  onSubmit,
}: {
  deptId: string
  onClose: () => void
  onSubmit: (data: any) => Promise<void>
}) {
  const [name, setName] = useState('')
  const [building, setBuilding] = useState('A')
  const [floor, setFloor] = useState('1')
  const [room, setRoom] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    try {
      await onSubmit({ department_id: deptId, name: name.trim(), building, floor, room })
    } finally {
      setSaving(false)
    }
  }

  return (
    <ModalWrapper title="Thêm Khu Vực / Vị Trí" onClose={onClose}>
      <form onSubmit={handleSubmit} style={{ padding: 20 }}>
        <div style={{ marginBottom: 14 }}>
          <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Tên Khu Vực / Vị Trí *</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Cổng Tiếp Đón, Hành Lang Cánh Đông..."
            style={inputStyle}
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 20 }}>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Tòa Nhà</label>
            <input value={building} onChange={(e) => setBuilding(e.target.value)} style={inputStyle} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Tầng</label>
            <input value={floor} onChange={(e) => setFloor(e.target.value)} style={inputStyle} />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>Số Phòng</label>
            <input value={room} onChange={(e) => setRoom(e.target.value)} placeholder="ER-01" style={inputStyle} />
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
          <button type="button" onClick={onClose} style={btnCancelStyle}>
            Hủy
          </button>
          <button type="submit" disabled={saving} style={btnSubmitStyle}>
            {saving ? <Loader size={14} className="animate-spin" /> : <CheckCircle2 size={14} />} Thêm
          </button>
        </div>
      </form>
    </ModalWrapper>
  )
}

function ModalWrapper({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
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
            padding: '14px 18px',
            background: '#0f172a',
            borderBottom: '1px solid #334155',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: '#f8fafc' }}>{title}</h3>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>
        {children}
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
