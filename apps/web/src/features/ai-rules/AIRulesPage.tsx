import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { aiRulesApi, camerasApi } from '../../services/api'
import {
  Brain,
  Plus,
  Trash2,
  Play,
  CheckCircle2,
  AlertCircle,
  X,
  Loader,
  Camera,
  ShieldAlert,
} from 'lucide-react'

const RULE_TYPE_LABELS: Record<string, string> = {
  restricted_area: 'Xâm nhập khu vực cấm',
  fall_detection: 'Cảnh báo té ngã',
  queue_estimation: 'Ùn tắc khu vực chờ (Dwell-time)',
  people_counting: 'Đếm lưu lượng người',
  camera_tamper: 'Phát hiện che / lệch ống kính',
  zone_monitoring: 'Giám sát vùng chuyên dụng',
}

export default function AIRulesPage() {
  const qc = useQueryClient()
  const [isAddRuleOpen, setIsAddRuleOpen] = useState(false)
  const [triggering, setTriggering] = useState(false)
  const [scanMessage, setScanMessage] = useState<string | null>(null)

  const { data: rules, isLoading } = useQuery({
    queryKey: ['ai-rules'],
    queryFn: () => aiRulesApi.list(),
  })

  const { data: camerasData } = useQuery({
    queryKey: ['cameras-all'],
    queryFn: () => camerasApi.list({ page_size: 100 }),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_enabled }: { id: string; is_enabled: boolean }) =>
      aiRulesApi.update(id, { is_enabled }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ai-rules'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => aiRulesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ai-rules'] }),
  })

  const handleManualScan = async () => {
    setTriggering(true)
    setScanMessage(null)
    try {
      const res = await aiRulesApi.triggerScan()
      setScanMessage(`Quét thành công! Phát hiện ${res.events_triggered} sự kiện cảnh báo.`)
      qc.invalidateQueries({ queryKey: ['events'] })
    } catch (err: any) {
      setScanMessage(`Lỗi quét: ${err.message || 'Không thể quét'}`)
    } finally {
      setTriggering(false)
    }
  }

  const cameras = camerasData?.items || []

  return (
    <div style={{ padding: 24, maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Brain size={26} color="#3b82f6" />
            Cấu hình Quy tắc Phân tích AI Computer Vision
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            Quản lý quy tắc nhận diện hành vi, xâm nhập và ùn tắc gắn theo từng camera ({rules?.length || 0} quy tắc)
          </p>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={handleManualScan}
            disabled={triggering}
            style={{
              background: '#334155',
              color: '#f8fafc',
              border: 'none',
              borderRadius: 8,
              padding: '10px 16px',
              fontSize: 13,
              fontWeight: 600,
              cursor: triggering ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            {triggering ? <Loader size={16} className="animate-spin" /> : <Play size={16} />}
            Quét AI Thủ Công Ngay
          </button>

          <button
            onClick={() => setIsAddRuleOpen(true)}
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
            <Plus size={16} /> Thêm Quy Tắc AI
          </button>
        </div>
      </div>

      {scanMessage && (
        <div
          style={{
            marginBottom: 20,
            padding: '10px 16px',
            background: '#064e3b33',
            border: '1px solid #059669',
            borderRadius: 8,
            color: '#34d399',
            fontSize: 13,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <CheckCircle2 size={16} />
          <span>{scanMessage}</span>
        </div>
      )}

      {/* Rules Grid */}
      {isLoading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Đang tải danh sách quy tắc AI...</div>
      ) : (rules || []).length === 0 ? (
        <div style={{ padding: 60, textAlign: 'center', background: '#1e293b', borderRadius: 10, border: '1px dashed #334155' }}>
          <Brain size={36} color="#64748b" style={{ margin: '0 auto 12px' }} />
          <p style={{ color: '#94a3b8', fontSize: 15, margin: '0 0 14px' }}>Chưa có quy tắc AI nào được thiết lập.</p>
          <button
            onClick={() => setIsAddRuleOpen(true)}
            style={{
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              padding: '8px 16px',
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Tạo quy tắc đầu tiên
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 16 }}>
          {rules?.map((rule: any) => {
            const cam = cameras.find((c) => c.id === rule.camera_id)
            return (
              <div
                key={rule.id}
                style={{
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: 12,
                  padding: 18,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600, color: '#f8fafc' }}>{rule.name}</div>
                      <div style={{ fontSize: 12, color: '#38bdf8', marginTop: 2 }}>
                        {RULE_TYPE_LABELS[rule.rule_type] || rule.rule_type}
                      </div>
                    </div>

                    <button
                      onClick={() => toggleMutation.mutate({ id: rule.id, is_enabled: !rule.is_enabled })}
                      style={{
                        background: rule.is_enabled ? '#064e3b33' : '#7f1d1d33',
                        border: `1px solid ${rule.is_enabled ? '#059669' : '#dc2626'}`,
                        color: rule.is_enabled ? '#34d399' : '#f87171',
                        borderRadius: 14,
                        padding: '2px 10px',
                        cursor: 'pointer',
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    >
                      {rule.is_enabled ? 'ĐANG BẬT' : 'TẠM TẮT'}
                    </button>
                  </div>

                  <div style={{ background: '#0f172a', borderRadius: 6, padding: '8px 12px', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#94a3b8' }}>
                    <Camera size={13} color="#38bdf8" />
                    <span>Áp dụng trên: <strong>{cam?.name || 'Camera ID: ' + rule.camera_id.slice(0, 8)}</strong></span>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, fontSize: 12, color: '#64748b' }}>
                    <span>Ngưỡng: <strong>{Math.round(rule.confidence_threshold * 100)}%</strong></span>
                    <span>• Cooldown: <strong>{rule.cooldown_seconds}s</strong></span>
                    <span>• Mức độ: <strong style={{ color: rule.severity === 'critical' ? '#ef4444' : '#f59e0b', textTransform: 'uppercase' }}>{rule.severity}</strong></span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid #334155', paddingTop: 12, marginTop: 14 }}>
                  <button
                    onClick={() => {
                      if (confirm(`Bạn có chắc muốn xóa quy tắc "${rule.name}"?`)) {
                        deleteMutation.mutate(rule.id)
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
                    <Trash2 size={13} /> Xóa quy tắc
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Add Rule Modal */}
      {isAddRuleOpen && (
        <AddRuleModal
          cameras={cameras}
          onClose={() => setIsAddRuleOpen(false)}
          onSuccess={() => {
            setIsAddRuleOpen(false)
            qc.invalidateQueries({ queryKey: ['ai-rules'] })
          }}
        />
      )}
    </div>
  )
}

function AddRuleModal({
  cameras,
  onClose,
  onSuccess,
}: {
  cameras: any[]
  onClose: () => void
  onSuccess: () => void
}) {
  const [name, setName] = useState('')
  const [cameraId, setCameraId] = useState(cameras[0]?.id || '')
  const [ruleType, setRuleType] = useState('restricted_area')
  const [severity, setSeverity] = useState('high')
  const [confidence, setConfidence] = useState(0.6)
  const [cooldown, setCooldown] = useState(30)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !cameraId) {
      setError('Vui lòng nhập tên quy tắc và chọn Camera áp dụng')
      return
    }

    setSaving(true)
    setError(null)
    try {
      await aiRulesApi.create({
        name: name.trim(),
        camera_id: cameraId,
        rule_type: ruleType,
        severity,
        confidence_threshold: Number(confidence),
        cooldown_seconds: Number(cooldown),
      })
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Lỗi tạo quy tắc')
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
          maxWidth: 520,
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
            <Brain size={18} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: '#f8fafc' }}>
              Thiết Lập Quy Tắc Phân Tích AI Mới
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: 20 }}>
          {error && (
            <div style={{ marginBottom: 14, padding: '8px 12px', background: '#7f1d1d33', border: '1px solid #dc2626', borderRadius: 6, color: '#f87171', fontSize: 12 }}>
              {error}
            </div>
          )}

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
              Tên Quy Tắc *
            </label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ví dụ: Giám sát xâm nhập phòng phẫu thuật sau 22:00..."
              style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
              Camera Áp Dụng *
            </label>
            <select value={cameraId} onChange={(e) => setCameraId(e.target.value)} style={inputStyle}>
              {cameras.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.ip_address ? `(${c.ip_address})` : ''}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Loại Quy Tắc
              </label>
              <select value={ruleType} onChange={(e) => setRuleType(e.target.value)} style={inputStyle}>
                <option value="restricted_area">Xâm nhập vùng cấm</option>
                <option value="fall_detection">Cảnh báo té ngã</option>
                <option value="queue_estimation">Ùn tắc khu vực chờ (Dwell)</option>
                <option value="people_counting">Đếm lưu lượng người</option>
                <option value="camera_tamper">Phát hiện che camera</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Mức Độ Nghiêm Trọng
              </label>
              <select value={severity} onChange={(e) => setSeverity(e.target.value)} style={inputStyle}>
                <option value="critical">CRITICAL (Khẩn cấp)</option>
                <option value="high">HIGH (Cao)</option>
                <option value="medium">MEDIUM (Trung bình)</option>
                <option value="low">LOW (Thấp)</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 18 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Ngưỡng Tin Cậy ({Math.round(confidence * 100)}%)
              </label>
              <input
                type="range"
                min="0.3"
                max="0.95"
                step="0.05"
                value={confidence}
                onChange={(e) => setConfidence(Number(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>
                Cooldown Chống Lặp (giây)
              </label>
              <input
                type="number"
                value={cooldown}
                onChange={(e) => setCooldown(Number(e.target.value))}
                style={inputStyle}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
            <button type="button" onClick={onClose} style={btnCancelStyle}>
              Hủy
            </button>
            <button type="submit" disabled={saving} style={btnSubmitStyle}>
              {saving ? <Loader size={14} className="animate-spin" /> : <CheckCircle2 size={14} />} Lưu Quy Tắc
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
